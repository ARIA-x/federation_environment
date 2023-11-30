import os, scp, paramiko


with open('sshenv') as f:
    lines = [x.strip() for x in f.readlines()]
    ssh_host = lines[0]
    ssh_port = lines[1]
    ssh_user = lines[2]
    ssh_pass = lines[3]


def DirSep():
    if os.name == "posix":
        #mac
        return "/"
    else:
        # windows
        return "\\"


def retrieve(_from, _to):
    scp_get(ssh_host, ssh_port, ssh_user, ssh_pass, _from=_from, _to=_to, _recursive=True)


def make_retrieve_dir(dir_path):
    CMD = "if [ ! -d %s ]; then mkdir -p %s; fi" % (dir_path, dir_path)
    ssh_exec(ssh_host, ssh_port, ssh_user, ssh_pass, CMD)


def takeover(outdir, indir):
    CMD = "if [ -d %s ]; then mv %s %s; fi" % (outdir, outdir, indir)
    print (CMD)
    ssh_exec(ssh_host, ssh_port, ssh_user, ssh_pass, CMD)


def make_dir(dir_path):
    CMD = "if [ ! -d %s ]; then mkdir -p %s; fi" % (dir_path, dir_path)
    ssh_exec(ssh_host, ssh_port, ssh_user, ssh_pass, CMD)


def rm_dir(dir_path):
    CMD = "rm -rf %s" % dir_path
    ssh_exec(ssh_host, ssh_port, ssh_user, ssh_pass, CMD)


def ssh_exec(host, port, user, pw, CMD):
    with paramiko.SSHClient() as _ssh:
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print('connect to host: ' + host + ':' + port)
        _ssh.connect(host, port=port, username=user, password=pw)

        print('Start ssh exec')
        stdin, stdout, stderr = _ssh.exec_command(CMD)
        for line in stdout:
            print(line, end='')
        for line in stderr:
            print(line, end='')


def scp_get(host, port, user, pw, _from=None, _to=None, _recursive=False):
    ## _recursive must be True in the case of directory transfer

    with paramiko.SSHClient() as _ssh:
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print('connect to host: ' + host + ':' + port)
        _ssh.connect(host, port=port, username=user, password=pw)

        print('Start scp get')
        # scp clientオブジェクト生成
        with scp.SCPClient(_ssh.get_transport()) as _scp:
            if _from == None or _to == None:
                print( 'from and to should be assinged FROM: %s, TO: %s' % _from, _to)
            else:
                _scp.get(_from, _to, recursive=_recursive)


def scp_put(host, port, user, pw, _from=None, _to=None, _recursive=False):
    ## _recursive must be True in the case of directory transfer

    with paramiko.SSHClient() as _ssh:
        _ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print('connect to host: ' + host + ':' + port)
        _ssh.connect(host, port=port, username=user, password=pw)

        print('Start scp put')
        # scp clientオブジェクト生成
        with scp.SCPClient(_ssh.get_transport()) as _scp:
            if _from == None or _to == None:
                print( 'from and to should be assinged FROM: %s, TO: %s' % _from, _to)
            else:
                _scp.put(_from, _to, recursive=_recursive)


# for test
if __name__ == '__main__':
    #scp_get('192.168.1.131', '22', 'docker', 'tcuser', '/data/pv0001/hoge', './')
    #scp_put('192.168.1.131', '22', 'docker', 'tcuser', 'test/test.sh', './')
    #ssh_exec('192.168.1.131', '22', 'docker', 'tcuser', 'mkdir -p /data/sim-a')
    make_retrieve_dir("/data/sim-d/out")
    #takeover("/data/sim-c/out", "/data/sim-b/in")