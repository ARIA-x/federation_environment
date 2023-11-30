import os
from pathlib import Path
from xmlrpc.client import Boolean

## kubernetes related libraries
from kubernetes import config, client
from kubernetes.client.exceptions import ApiException
from kubernetes.client.api import core_v1_api

## Simulation libraries
from simulation.configparse import SimulationConfig
import runsh, sim_utils, docker_client, k8s_client, k8s_exec


class Simulation:
 
    def __init__(self):
        self.config    = SimulationConfig()
        self.take_over = False

    def run(self, next_sim=None):
        print("===================================================")
        print("== Start Simulation ")
        print("== Name: " + self.config.getName())
        print("== Next: " + str(next_sim))
        if not self.config.ready():
            print("Not ready to run: no path or cmdline")
            print("path    :", self.config.getPath())
            print("cmdline :", self.config.getCmdline())
            return False

        ## create run.sh script
        print("----------- create run.sh script -----------------")
        filename = Path(self.config.getPath() + "/run.sh")
        filename.touch(exist_ok=True)
        with open(filename, "wb") as f:
            #s = runsh.mkscript(self.config.getCmdline())
            s = runsh.mkscript(self.config, self.take_over)
            f.write(s.encode('utf-8'))
        print( '> create run.sh in ' + str(filename))

        ## create image file
        print("--------- create docker image file ---------------")
        dockerfile = docker_client.create_dockerfile(
            baseimage=self.config.getBaseImage(),
            # simdir=self.config.getPath(),
            # workdir=self.config.getWorkDir(),
            update=self.config.getUpdate()
        )
        print (dockerfile)
        resp = docker_client.build_image(dockerfile, 'app/sim')
        for line in resp:
            print(line)

        cfg = config.load_kube_config()
        with client.ApiClient(cfg) as api_client:
            api = client.CoreV1Api(api_client)

            namespace = 'default'
            output_directory = "/data/" + self.config.getName() + "/out"

            #if self.take_over != None:
            #    input_directory = "/data/" + self.config.getName() + "/in"
            
            ## create retrieve directory in kubernetes cluster
            sim_utils.make_retrieve_dir(output_directory)

            ## create Persistent Volume
            print("--------- create persistent volume ---------------")
            try:
                k8s_client.create_pv(api, "local-pv", "/data")
            except ApiException as ex:
                if ex.reason == 'Conflict':
                    print("already exists.")
                else:
                    print(ex)

            ## create Persistent Volume Claim
            print("------ create persistent volume claim ------------")
            try:
                k8s_client.create_pvc(api, "local-pvc", namespace)
            except ApiException as ex:
                if ex.reason == 'Conflict':
                    print("already exists.")
                else:
                    print(ex)

            ## create Pod
            print("---------------  create Pod ----------------------")
            core_V1 = k8s_exec.create_pod_session(self.config.getName(), "app/sim", "local-pvc")

            '''
            ## We shold use deployment and service when we want to connect 
            ## simulators inside kubernetes to an external system.
            ## ARIA3D and MinHina are typical cases.
            ## TODO: prepare specifications to use deployment and service

            print("------------- create Deployment ------------------")
            try:
                apps_api = client.AppsV1Api(api_client)
                k8s_client.create_deployment(apps_api, "sim", "python", {"app":"simu"}, "local-pvc", namespace)
            except ApiException as ex:
                if ex.reason == 'Conflict':
                    print("already exists.")
                else:
                    print(ex)
            '''
            ## copy simulator in the pod
            print("------- copy the simulator in the pod ------------")
            k8s_exec.copy_to_pod(self.config.getName(), core_V1, self.config.getPath(), self.config.getWorkDir())

            ## create a link from result directory to persistent volume
            #cmd = [
            #    "/bin/sh",
            #    "-c",
            #    "ln -s /data/" + self.config.getName() + " " + self.config.getOutdir()]
            #resp = k8s_exec.exec_commands(self.config.getName(), core_V1, exec_command=cmd)

            ## run simulation
            print("---------------- run simulation ------------------")
            cmd = [
                "/bin/sh",
                "-c",
                "cd " + self.config.getWorkDir() + "; /bin/sh run.sh"]
            resp = k8s_exec.exec_commands(self.config.getName(), core_V1, exec_command=cmd)
            print("Response: " + resp)

            ## retrieve the results
            print("------------- retrieve the results ---------------")
            # retrieve data
            sim_utils.retrieve(output_directory, self.config.getRetrieve())

            if next_sim != None:
                ## take over the simulation result to next
                next_input = "/data/" + next_sim + "/in/"
                sim_utils.make_dir("/data/" + next_sim)
                sim_utils.takeover(output_directory, next_input)
            sim_utils.rm_dir("/data/"+self.config.getName())

            print("------------------ delete pod --------------------")
            k8s_exec.delete_pods(self.config.getName())

        return True


    def path(self, path):
        self.config.path = path


    def cmdline(self, cmdline):
        a = cmdline.split()
        self.config.setCmd(a[0])
        self.config.setArgs(a[1:])

    def setconfig(self, configfile):
        self.config.read(configfile)

    def takeOver(self):
        self.take_over = True
    