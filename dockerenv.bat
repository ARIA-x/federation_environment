minikube docker-env

echo %DOCKER_TLS_VERIFY% >> dockerenv
echo %DOCKER_HOST% >> dockerenv
echo %DOCKER_CERT_PATH% >> dockerenv
echo %MINIKUBE_ACTIVE_DOCKERD% >> dockerenv