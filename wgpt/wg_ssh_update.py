import paramiko
import io

from wgpt import models


def send_ssh_command(command, known_host, pubkey, ip):
    if command == "add":
        ssh_command = "sudo wg set wg0 peer {} allowed-ips {}/32".format(pubkey, ip)
    elif command == "remove":
        ssh_command = "sudo wg set wg0 peer {} remove allowed-ips {}/32".format(pubkey, ip)

    conf = models.ConfigOptions.query.all()[0]

    print(ssh_command)

    ssh = paramiko.SSHClient()
    hostkey = paramiko.hostkeys.HostKeyEntry.from_line(known_host)

    ssh.get_host_keys().add(hostkey.hostnames[0], hostkey.key.get_name(), hostkey.key)

    try:
        ssh.connect(hostkey.hostnames[0],
                    username='wgpt',
                    pkey=paramiko.RSAKey(file_obj=io.StringIO(conf.ssh_privkey)))
    except paramiko.AuthenticationException:
        return False 
    
    try:
        stdin, stdout, stderr = ssh.exec_command(ssh_command)
    except paramiko.SSHException:
        return False 

    data = stderr.readlines()
    for line in data:
        print(line.strip())
    ssh.close()
    return True
