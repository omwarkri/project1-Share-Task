#!/usr/bin/env bash
set -euo pipefail

echo "Deleting Kubernetes resources in k8s/ (ignore not found)..."
kubectl delete -f k8s/ --ignore-not-found

echo "Stopping and deleting minikube (if running)..."
minikube stop || true
minikube delete || true

echo "If Jenkins was started via Docker, stop the container:"
echo "  docker stop jenkins || true"

echo "Teardown complete."
