#!/usr/bin/env bash
set -euo pipefail

# Start minikube, build image into minikube, apply k8s manifests

echo "Starting minikube (docker driver)..."
minikube start --driver=docker

echo "Building image into minikube: share-task-web:latest"
minikube image build -t share-task-web:latest -f todolist/Dockerfile .

echo "Applying Kubernetes manifests from k8s/"
kubectl apply -f k8s/

echo "Waiting for deployment to become available (timeout 120s)..."
kubectl wait --for=condition=available deployment/todolist-app -n todolist --timeout=120s || true

echo "Service URL (NodePort):"
minikube service todolist-service -n todolist --url || true
