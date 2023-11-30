from sys import api_version
import time, tarfile, tempfile

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client import V1DeleteOptions
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream



## fixed variables
cmd       = ["/bin/sh", "-c", "while true;do date;sleep 5; done"]


def copy_to_pod(podname, api_instance, filename, dst):
    print(filename)
    # Copying file
    exec_command = ['tar', 'xvf', '-', '-C', '/']
    resp = stream(api_instance.connect_get_namespaced_pod_exec, podname, 'default',
                command=exec_command,
                stderr=True, stdin=True,
                stdout=True, tty=False,
                _preload_content=False)

    with tempfile.TemporaryFile() as tar_buffer:
        ## create a tarball
        with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
            tar.add(filename, arcname=dst) ## directory name is also O.K.    
        tar_buffer.seek(0)

        commands = []
        commands.append(tar_buffer.read())

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                print("STDOUT: %s" % resp.read_stdout())
            if resp.peek_stderr():
                print("STDERR: %s" % resp.read_stderr())
            if commands:
                c = commands.pop(0)
                resp.write_stdin(c)
            else:
                break
        resp.close()


def exec_commands(name, api_instance, interactive=False, exec_command=None):
    resp = None
    if interactive:
    # Calling exec interactively
        exec_command = ['/bin/sh']
        resp = stream(api_instance.connect_get_namespaced_pod_exec,
                      name,
                      'default',
                      command=exec_command,
                      stderr=True, stdin=True,
                      stdout=True, tty=False,
                      _preload_content=False)
    else:
    # Calling exec and waiting for response
        if exec_command == None:
            print("command line must be needed in non-interactive mode")
        else:
            resp = stream(api_instance.connect_get_namespaced_pod_exec,
                          name,
                          'default',
                          command=exec_command,
                          stderr=True, stdin=False,
                          stdout=True, tty=False)
    return resp


def create_pod_session(name, image, pvc_name=None):
    config.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()

    ## create an instance
    resp = None

    try:
        resp = core_v1.read_namespaced_pod(name=name, namespace='default')
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)

    if not resp:
        print("Pod %s does not exist. Creating it..." % name)

        c_info = {
            'image': image,
            'imagePullPolicy' : 'IfNotPresent',
            'name': name+'1',
            'args': cmd}
        s_info = {
            'containers': [c_info]}

        if pvc_name != None:
            v_info = {
                'name' : 'claim-volume',
                'persistentVolumeClaim': {'claimName': pvc_name}}
            c_info['volumeMounts'] = [{'name': 'claim-volume', 'mountPath': '/data'}]
            s_info['volumes'] = [v_info]

        pod_manifest = {
            'metadata': {'name': name},
            'apiVersion': 'v1',
            'kind': 'Pod',
            'spec': s_info}

        # print(pod_manifest)

        resp = core_v1.create_namespaced_pod(body=pod_manifest, namespace='default')
        while True:
            resp = core_v1.read_namespaced_pod(name=name, namespace='default')
            # print(resp)
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        print("Done.")
    else:
        print("already exists.")
    return core_v1

'''
            {
                'containers': [{
                    'image': image,
                    'name': 'sleep',
                    'args': [
                        "/bin/sh",
                        "-c",
                        "while true;do date;sleep 5; done"
                    ],
                    'volumeMounts': [{
                        'name': 'claim-volume',
                        'mountPath': '/data'
                    }]
                }],
                'volumes': [{
                    'name': 'claim-volume',
                    'persistentVolumeClaim': {
                        'claimName': 'local-pvc'
                    }
                }]
            }
'''


def delete_pods(name, ns="default", label_selector=None):
    """
    The pods are deleted without a graceful period to trigger an abrupt
    termination. The selected resources are matched by the given `label_selector`.
    """
    config.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()

    if label_selector:
        ret = core_v1.list_namespaced_pod(ns, label_selector=label_selector)
    else:
        ret = core_v1.list_namespaced_pod(ns)
        ret.items = [p for p in ret.items if p.metadata.name == name]

    print("Found {d} pods named '{n}'".format(d=len(ret.items), n=name))

    if len(ret.items) != 0:
        body = V1DeleteOptions(grace_period_seconds=0)
        for p in ret.items:
            print("trying to terminate a Pod: " + p.metadata.name)
            core_v1.delete_namespaced_pod(p.metadata.name, ns, body=body) 



def main():
    name  = 'sim-test'
    image = 'sim'

    # Create or access existing pod
    core_v1 = create_pod_session(name, image)


    cmd = [
        '/bin/sh',
        '-c',
        'echo This message goes to stderr; echo This message goes to stdout']

    # Calling exec and waiting for response
    resp = exec_commands(name, core_v1, exec_command=cmd)
    print("Response: " + resp)

    # Calling exec and waiting for response
    resp = exec_commands(name, core_v1, interactive=True)
    commands = [
        "echo This message goes to stdout",
        "echo \"This message goes to stderr\" >&2",
    ]

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print("STDOUT: %s" % resp.read_stdout())
        if resp.peek_stderr():
            print("STDERR: %s" % resp.read_stderr())
        if commands:
            c = commands.pop(0)
            print("Running command... %s\n" % c)
            resp.write_stdin(c + "\n")
        else:
            break

    resp.write_stdin("date\n")
    sdate = resp.readline_stdout(timeout=3)
    print("Server date command returns: %s" % sdate)
    resp.write_stdin("whoami\n")
    user = resp.readline_stdout(timeout=3)
    print("Server user is: %s" % user)
    resp.close()


    copy_to_pod(name, core_v1, './test', '/test')
    cmd = [
        '/bin/sh',
        'test/test.sh']
    # Calling exec and waiting for response
    resp = exec_commands(name, core_v1, exec_command=cmd)
    print("Response: " + resp)

    #delete_pods(name)


if __name__ == '__main__':
    main()