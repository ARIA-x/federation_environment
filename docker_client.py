from io import BytesIO
from posixpath import basename

import docker
import sim_utils


with open('dockerenv') as f:
    lines = [x.strip() for x in f.readlines()]
    docker_tls_verify = int(lines[0])
    docker_host       = lines[1]
    docker_cert_path  = lines[2] + sim_utils.DirSep()
    docker_active_dockerd = lines [3]


tls_config = docker.tls.TLSConfig(
    verify=docker_cert_path + "ca.pem", 
    client_cert=(docker_cert_path + "cert.pem", 
                 docker_cert_path + "key.pem")
    )

'''
tls_config = docker.tls.TLSConfig(
    verify="C:\\Users\\kohig\\.minikube\\certs\\ca.pem", 
    client_cert=("C:\\Users\\kohig\\.minikube\\certs\\cert.pem", 
                 "C:\\Users\\kohig\\.minikube\\certs\\key.pem")
    )
'''

def create_dockerfile(baseimage=None, simdir=None, outdir=None, workdir=None, update=False):
    '''
    if simdir == None:
        print("A directory name should be assigned to simdir parameter at least")
        return
    '''
    if baseimage == None:
        baseimage = "busybox:latest"
    
    lines = []
    lines.append("FROM " + baseimage)
    if update:
        lines.append("RUN apt upgrade")
    #lines.append("ADD " + simdir + " ." )
    if outdir != None:
        lines.append("VOLUME " + outdir)
    lines.append("VOLUME /data")
    if workdir != None:
        lines.append("WORKDIR " + workdir)
    #lines.append("CMD ['/bin/sh']")
    return "\n".join(lines)

def build_image(dockerfile, tag):
    client = docker.DockerClient(base_url=docker_host, tls=tls_config)
    f = BytesIO(dockerfile.encode('utf-8'))
    return client.api.build(fileobj=f, rm=True, tag=tag)
    

if __name__ == "__main__":
    client = docker.DockerClient(base_url=docker_host, tls=tls_config)

    dockerfile = create_dockerfile(baseimage="python", update=True)
    print(dockerfile)
    
    '''
    dockerfile =  
    # Shared Volume
    FROM busybox:buildroot-2014.02
    VOLUME /data
    CMD ["/bin/sh"]
    '''

    resp = build_image(dockerfile, "sim")
    for line in resp:
        print(line)
    print(client.images.list())
    

