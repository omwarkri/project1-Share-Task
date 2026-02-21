# Share-Task — Simplified local run guide

Overview
- This repo contains a Django app (`todolist/`) and Kubernetes manifests in `k8s/`.
- The goal: run Jenkins locally and run the app on Minikube (NodePort) with minimal steps.

Prerequisites
- Linux or macOS with Docker installed
- `minikube`, `kubectl`, and `docker` available on PATH
- Optional: `systemd` with `jenkins` service (or Docker to run Jenkins container)

Quick Start

1) Start Jenkins (preferred: system service)

If you have `jenkins` installed as a systemd service:

```bash
sudo systemctl start jenkins
sudo systemctl status jenkins --no-pager
```

Or run Jenkins in Docker:

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

2) Start Minikube, build image and deploy the app

Use the helper script:

```bash
./scripts/run-minikube.sh
```

What the script does:
- starts minikube (docker driver)
- builds the app image `share-task-web:latest` into minikube
- applies manifests in `k8s/` (namespace and resources included)
- prints the NodePort service URL (NodePort 30080)

3) Access the app

- If `minikube service` prints a URL, open it in your browser (example: `http://192.168.49.2:30080`).
- Jenkins (if started via systemd or Docker) will be at `http://localhost:8080`.

Troubleshooting
- If an initContainer fails with "python: can't open file '/app/manage.py'": make sure your Dockerfile copies the Django project into `/app` and that build context includes the application files. The repo contains `todolist/Dockerfile` — build with the repository root as context.
- To rebuild the image manually:

```bash
minikube image build -t share-task-web:latest -f todolist/Dockerfile .
kubectl rollout restart deployment/todolist-app -n todolist || kubectl apply -f k8s/
```

Teardown

Use the helper script:

```bash
./scripts/teardown.sh
```

If you need more help, open the `todolist/` Dockerfile and check where files are copied into the container.
