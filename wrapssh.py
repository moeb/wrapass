#/usr/bin/env python3

import re
import sys
import time
import pexpect
import subprocess

def shh_pass(base_cmd):
    """
    use ssh with pass password manager
    base_cmd: 'ssh' or 'scp' or whatever command has user@host as argument and expects a passwd
    """
    # get user and host
    cmdline = sys.argv[1:][0]
    result = re.search("(?P<user>\w+)@(?P<host>[a-zA-Z0-9\._-]+)", cmdline)
    dct = result.groupdict()
    user = dct['user']
    host = dct['host']
    userhost = user+"@"+host

    if not user or not host:
        print("missing user or host")
        sys.exit(0)
    result = subprocess.run(["/usr/bin/pass",
                             "show",
                             "ssh/"+userhost],
                            capture_output=True)
    if result.returncode == 1:
        # failed to find ssh/user@host
        # in password store
        print(userhost, "is not in the password store!")
        sys.exit(1)
    # found key in the password store
    passwd = result.stdout
    # create ssh cmd
    args = list(sys.argv[1:])
    args.insert(0, base_cmd)
    # spawn ssh
    ssh = pexpect.spawn(" ".join(args))
    # supply password
    ssh.expect("password:")
    time.sleep(0.1)
    ssh.sendline(passwd)
    # yeah done :)
    ssh.interact()
