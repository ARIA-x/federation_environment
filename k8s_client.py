from kubernetes import config, client
from kubernetes.client.rest import ApiException


# 永続ボリュームの作成
def create_pv(api, volumename, path):
    pv = client.V1PersistentVolume()
    # 永続ボリューム名
    pv.metadata = client.V1ObjectMeta(name=volumename)
    pv.spec = client.V1PersistentVolumeSpec(
        # 容量
        capacity = {"storage":"50Mi"},
        # local volume
        local = client.V1LocalVolumeSource(path=path),
        # アクセスモード
        access_modes = ["ReadWriteOnce"],
            # node affinityの設定
        node_affinity = client.V1VolumeNodeAffinity(
            required = client.V1NodeSelector(
                node_selector_terms = [
                    client.V1NodeSelectorTerm(
                        match_expressions = [
                            client.V1NodeSelectorRequirement(
                                key = "kubernetes.io/hostname",
                                operator = "In",
                                values = ["minikube"] # 適宜ホスト名を変更してください
                            )
                        ]
                    )
                ]
            )
        ),
        # storage class設定
        storage_class_name = "local-storage",
    )
    api.create_persistent_volume(pv)


# 永続ボリューム要求の作成
def create_pvc(api, pvc_name, namespace):
    pv = client.V1PersistentVolumeClaim()
    pv.metadata = client.V1ObjectMeta(name=pvc_name)
    pv.spec = client.V1PersistentVolumeClaimSpec(
        access_modes = ["ReadWriteOnce"],
        resources = client.V1ResourceRequirements(
            requests = {"storage": "50Mi"}
        ),
        storage_class_name = "local-storage",
    )
    api.create_namespaced_persistent_volume_claim(namespace, pv)


# Deploymentの作成
def create_deployment(api, deploy_name, image, label, pvc, namespace):
    # TODO: Podを引数に取る場合も記載する
    dp = client.V1Deployment()
    dp.metadata = client.V1ObjectMeta(
        name=deploy_name,
        labels=label
    )
    dp.spec = client.V1DeploymentSpec(
        replicas = 1,
        selector = client.V1LabelSelector(match_labels=label),
        template = client.V1PodTemplateSpec(
            metadata = client.V1ObjectMeta(labels=label),
            spec = client.V1PodSpec(
                containers = [
                    client.V1Container(
                        name = "mypod",
                        image = image,
                        ports = [client.V1ContainerPort(container_port=80)],
                        volume_mounts = [
                            client.V1VolumeMount(
                                name = pvc,
                                mount_path = "/data"
                            )
                        ],
                        command = ["tail", "-f", "/dev/null"]
                        ## tiny linux distros are halted just after bootup if there are no command to execute.
                        ## So, some commands should keep running when you use the above distros.
                    )
                ],
                volumes = [
                    client.V1Volume(
                        name = pvc,
                        persistent_volume_claim = client.V1PersistentVolumeClaimVolumeSource(
                        claim_name = pvc
                        )
                    )
                ]
            )
        )
    )
    api.create_namespaced_deployment(namespace, dp)


# Serviceの作成
def create_service(api, service_name, namespace):
    sv = client.V1Service()
    sv.metadata = client.V1ObjectMeta(name=service_name)
    sv.spec = client.V1ServiceSpec(
        selector = {"app":"myhttpd"},
        type = "LoadBalancer",
        external_i_ps = ["192.168.1.119"], # 適宜IPアドレスを変更してください
        ports = [
            client.V1ServicePort(
                port = 8080,      # 外部公開するポート番号
                target_port = 80, # コンテナがサービスを展開しているポート番号
                protocol = "TCP"
            )
        ]
    )
    api.create_namespaced_service(namespace, sv)


if __name__ == "__main__":
    # configを読み込み
    cfg = config.load_kube_config()

    # クライアントを作成
    with client.ApiClient(cfg) as api_client:
        api = client.CoreV1Api(api_client)
        namespace = 'default'
        # 永続ボリュームの作成
        try:
            create_pv(api, "local-pv", "/data")
        except ApiException as ex:
            if ex.reason == 'Conflict':
                print("already exists.")
            else:
                print(ex)

        # 永続ボリューム要求の作成
        try:
            create_pvc(api, "local-pvc", namespace)
        except ApiException as ex:
            if ex.reason == 'Conflict':
                print("already exists.")
            else:
                print(ex)

        # Deploymentの作成
        try:
            apps_api = client.AppsV1Api(api_client)
            create_deployment(apps_api, "test-deployment", "alpine", {"app":"testapp"}, "local-pvc", namespace)
        except ApiException as ex:
            if ex.reason == 'Conflict':
                print("already exists.")
            else:
                print(ex)



        '''
        # Serviceの作成
        try:
            create_service(api, "httpd-service", namespace)
        except ApiException as ex:
            if ex.reason == 'Conflict':
                print("already exists.")
            else:
                print(ex)
        '''