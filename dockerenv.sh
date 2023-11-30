#!/bin/bash

eval $(minikube -p minikube docker-env)

touch dockerenv

echo $DOCKER_TLS_VERIFY >> dockerenv
echo $DOCKER_HOST >> dockerenv
echo $DOCKER_CERT_PATH >> dockerenv
echo $MINIKUBE_ACTIVE_DOCKERD >> dockerenv