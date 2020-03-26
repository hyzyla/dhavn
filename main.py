import select
import socket
import sys
import threading

from loguru import logger
from paramiko import AutoAddPolicy, Channel, ChannelFile, SSHClient, Transport
from paramiko.auth_handler import AuthenticationException

logger.add(sys.stderr, format="{time} {message}", filter="client", level="INFO")
logger.add(
    "logs/log_{time:YYYY-MM-DD}.log",
    format="{time} {level} {message}",
    filter="client",
    level="ERROR",
)

HOST = '68.183.208.150'
USER = 'root'
SSH_KEY_PATH = '~/.ssh/id_rsa.pub'

LOCALHOST = '127.0.0.1'


class RemoteClient:

    def __init__(self, host, user, remote_path):
        self.host = host
        self.user = user
        self.remote_path = remote_path
        self.client = None

    def connect(self):
        try:
            self.client = SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(self.host, username=self.user, timeout=5000)

        except AuthenticationException as error:
            logger.info("Authentication failed: did you remember to create an SSH key?")
            logger.error(error)
            raise error
        finally:
            return Connection(self.client)

    def disconnect(self):
        self.client.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


def forwarder(channel: Channel, local_port: int):

    # connect to localhost via sockets
    sock = socket.socket()
    try:
        sock.connect((LOCALHOST, local_port))
    except Exception as e:
        logger.error(f'Forwarding request to {local_port} failed: e')
        return

    # read data from channel or socket and send to opposite site
    while True:
        r, _, _ = select.select([sock, channel], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            channel.send(data)
        if channel in r:
            data = channel.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    channel.close()
    sock.close()
    logger.info(f'Tunnel closed from {channel.origin_addr}')


class Connection:
    def __init__(self, client: SSHClient):
        self.client: SSHClient = client

    def execute_commands(self, cmd):
        stdin: ChannelFile
        stdout: ChannelFile
        stderr: ChannelFile

        stdin, stdout, stderr = self.client.exec_command(cmd)
        stdout.channel.recv_exit_status()

        for line in stdout:
            logger.info(f"STDIN: {cmd} | STDOUT: {line}")
        for line in stderr:
            logger.info(f"STDIN: {cmd} | STDERR: {line}")

    def right_forwarding(self):
        transport: Transport = self.client.get_transport()
        transport.request_port_forward('127.0.0.1', port=10001)

        while True:

            # wait 2 seconds for new channel
            channel: Channel = transport.accept(timeout=10)
            if channel is None:
                continue

            # Handle new channel and forward traffic to local port
            # TODO: create new tread for handling channel connection
            forwarder(channel, local_port=8000)


def main():
    client = RemoteClient(
        host=HOST,
        user=USER,
        remote_path='/root',
    )

    with client as conn:
        conn.execute_commands('pwd')

        # Run right forwarding in background
        r_forward_thread = threading.Thread(target=conn.right_forwarding)
        r_forward_thread.run()

        # conn.execute_commands('lsof -i -P -n')
        conn.execute_commands('curl 127.0.0.1:10000')
        # conn.execute_commands(
        #     'sshfs '
        #     '-p 10000 '
        #     '-o idmap=user,nonempty '
        #     'y.hyzyla@localhost:/home/y.hyzyla/Work/dhavn workdir'
        # )

        # conn.r_forward()
        # TODO: Add direct and revert port forwarding
        # TODO: mount local directory with sshfs


if __name__ == '__main__':
    main()
