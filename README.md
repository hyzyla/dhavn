## dhavn

1) Create droplet/vm/etc
2) (REMOTE) Install docker and sshfs
3) Connect with port forwarding
```shell script
ssh root@68.183.208.150 -R 10000:yhyzyla:22 -L 5000:localhost:5000
```

4) Connect to local directory (ssh server on local machine is required)
```shell script
sshfs -p 10000 -o idmap=user,nonempty y.hyzyla@localhost:/home/y.hyzyla/Work/dhavn workdir
```

5) Open localhost:5000 in browser
