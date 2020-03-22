import sys

from loguru import logger
from paramiko import AutoAddPolicy, SSHClient
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
            return self.client

    def disconnect(self):
        self.client.close()

    def execute_commands(self, cmd):
        if self.client is None:
            self.connect()

        stdin, stdout, stderr = self.client.exec_command(cmd)
        stdout.channel.recv_exit_status()
        response = stdout.readlines()
        for line in response:
            logger.info(f"INPUT: {cmd} | OUTPUT: {line}")

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


if __name__ == '__main__':
    client = RemoteClient(
        host=HOST,
        user=USER,
        remote_path='/root',
    )

    with client:
        client.execute_commands('pwd')
        # TODO: Add direct and revert port forwarding
        # TODO: mount local directory with sshfs
