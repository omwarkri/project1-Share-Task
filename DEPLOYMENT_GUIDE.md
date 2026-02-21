# Complete Deployment Pipeline Guide
## Local Development to Monitoring with Prometheus + Grafana

---

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Developer & GitHub Setup](#phase-1-developer--github-setup)
4. [Phase 2: Jenkins CI/CD Setup](#phase-2-jenkins-cicd-setup)
5. [Phase 3: Docker Build & Local Registry](#phase-3-docker-build--local-registry)
6. [Phase 4: Kubernetes Deployment](#phase-4-kubernetes-deployment)
7. [Phase 5: Monitoring (Prometheus + Grafana)](#phase-5-monitoring-prometheus--grafana)
8. [Complete Workflow](#complete-workflow)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Developer    →    GitHub      →    Jenkins CI/CD               │
│    (Commit)      (Repository)      (Automated Build)            │
│                                          ↓                       │
│                                    Docker Build                  │
│                                    (Create Image)               │
│                                          ↓                       │
│                              Local Docker Registry              │
│                              (Store Image)                      │
│                                          ↓                       │
│                M inikube (Kubernetes Local Cluster)             │
│            ┌──────────────────────────────────────┐            │
│            │  • Deployment (2 replicas)           │            │
│            │  • Service (NodePort 30080)          │            │
│            │  • Ingress                           │            │
│            │  • Namespace (todolist)              │            │
│            └──────────────────────────────────────┘            │
│                                          ↓                       │
│            Monitoring & Observability                            │
│            ┌──────────────────────────────────────┐            │
│            │  • Prometheus (Metrics Collection)   │            │
│            │  • Grafana (Visualization)           │            │
│            │  • Node Exporter                     │            │
│            │  • cAdvisor (Container Metrics)      │            │
│            └──────────────────────────────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

Before starting, ensure you have these tools installed:

### Required Software
```bash
# Check if installed
which git
which docker
which kubectl
which minikube
which helm          # Optional, for Prometheus/Grafana

# Install Docker (if not already installed)
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Minikube (Kubernetes)
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl (Kubernetes CLI)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm (Package Manager for Kubernetes)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### System Requirements
- **RAM**: At least 4GB (8GB recommended for Prometheus + Grafana + Minikube)
- **Disk Space**: 20GB free space
- **CPU**: 2+ cores preferred
- **Linux/Mac** (WSL2 on Windows)

### Verify Installation
```bash
docker --version
docker-compose --version
kubectl version --client
minikube version
helm version
```

---

## Phase 1: Developer & GitHub Setup

### Step 1.1: Clone the Repository
```bash
# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/share-task.git
cd share-task

# Or initialize a new repository
git init
git remote add origin https://github.com/YOUR_USERNAME/share-task.git
```

### Step 1.2: Setup Git Credentials
```bash
# Configure Git (one-time setup)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# For HTTPS (recommended for beginners)
git config --global credential.helper store

# For SSH (advanced)
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub  # Copy this to GitHub > Settings > SSH Keys
```

### Step 1.3: Create Feature Branch & Commit Code
```bash
# Create a new feature branch
git checkout -b feature/my-new-feature

# Make your changes to the code
# Edit files in todolist/ directory

# Stage your changes
git add .

# Commit with meaningful message
git commit -m "feat: Add new task creation feature"

# Push to GitHub
git push origin feature/my-new-feature
```

### Step 1.4: Create Pull Request (Optional)
```bash
# On GitHub.com:
# 1. Go to your repository
# 2. Click "Compare & pull request"
# 3. Add description of changes
# 4. Click "Create pull request"
```

### Step 1.5: Merge to Main Branch
```bash
# After review/approval, merge to main
# Option A: Via GitHub web interface
# Click "Merge pull request" button

# Option B: Via Git CLI
git checkout main
git pull origin main
git merge feature/my-new-feature
git push origin main
```

---

## Phase 2: Jenkins CI/CD Setup

### Step 2.1: Start Jenkins

#### Option A: Jenkins as System Service (Linux)
```bash
# Install Jenkins (if not already installed)
# Ubuntu/Debian
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install -y jenkins

# Start Jenkins service
sudo systemctl start jenkins
sudo systemctl enable jenkins  # Auto-start on reboot
sudo systemctl status jenkins

# Access Jenkins at http://localhost:8080
# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

#### Option B: Jenkins in Docker (Easier for Local Testing)
```bash
# Create Jenkins data directory
mkdir -p ~/jenkins_home

# Start Jenkins container
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v ~/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# Wait for startup (30 seconds)
sleep 30

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Access Jenkins at http://localhost:8080
```

### Step 2.2: Initial Jenkins Configuration

1. **Open Jenkins**: Visit `http://localhost:8080`
2. **Unlock Jenkins**: Paste the initial admin password
3. **Install Recommended Plugins**:
   - Click "Install suggested plugins"
   - Wait for installation (~10 minutes)
4. **Create Admin User**:
   - Fill in username, password, email
   - Click "Save and Continue"
5. **Configure Jenkins URL**:
   - Set to `http://localhost:8080`
   - Click "Save and Finish"

### Step 2.3: Install Required Jenkins Plugins

Go to **Manage Jenkins** → **Plugin Manager** → **Available** tab. Search and install:

```
- Docker Pipeline
- Kubernetes
- GitHub Integration
- Git
- Pipeline
- Blue Ocean (optional, for better UI)
- Email Extension
```

### Step 2.4: Configure Jenkins Credentials

1. Go to **Manage Jenkins** → **Manage Credentials** → **System** → **Global credentials**
2. Click **Add Credentials**
3. **Add GitHub SSH Key**:
   - Kind: SSH Username with private key
   - Username: `git`
   - Private Key: Paste your GitHub SSH private key (`~/.ssh/id_ed25519`)
   - ID: `github-ssh`

4. **Add Docker Registry Credentials**:
   - Kind: Username with password
   - Username: (your Docker Hub username or local registry)
   - Password: (your Docker Hub token or password)
   - ID: `docker-registry`

### Step 2.5: Create Jenkins Pipeline Job

1. **Create New Job**:
   - Click "New Item"
   - Enter name: `share-task-pipeline`
   - Select "Pipeline"
   - Click "OK"

2. **Configure Pipeline**:
   - Under "Pipeline" section
   - Select "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `https://github.com/YOUR_USERNAME/share-task.git`
   - Credentials: Select your GitHub credentials
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
   - Click "Save"

### Step 2.6: Trigger Pipeline

```bash
# Option A: Manual Trigger
# In Jenkins UI: Click "Build Now" button

# Option B: Automatic Trigger (Webhook)
# 1. Go to GitHub repository Settings → Webhooks
# 2. Click "Add webhook"
# 3. Payload URL: http://YOUR_IP:8080/github-webhook/
# 4. Select "Push events"
# 5. Click "Add webhook"
# Now Jenkins will automatically build on every push to main

# Option C: Command Line Trigger
curl -X POST http://localhost:8080/job/share-task-pipeline/build \
  --user admin:YOUR_API_TOKEN
```

### Step 2.7: Monitor Pipeline Execution

1. In Jenkins, click on the job name `share-task-pipeline`
2. Click on the job number (e.g., #1) to see build details
3. Click "Console Output" to see build logs
4. Wait for successful completion (Green checkmark)

---

## Phase 3: Docker Build & Local Registry

### Step 3.1: Understand Dockerfile

Your project includes a multi-stage Dockerfile:

```dockerfile
# Stage 1: Builder - compile dependencies
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev
COPY todolist/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production - minimal runtime image
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq5 postgresql-client
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY todolist/ /app/
EXPOSE 8000
CMD ["gunicorn", "todolist.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Step 3.2: Build Docker Image Locally

```bash
# Navigate to project root
cd /home/om/Desktop/Share-Task

# Build image with tag
docker build -t share-task-web:latest -f todolist/Dockerfile .

# Tag image for registry (format: registry/repository:tag)
docker tag share-task-web:latest localhost:5000/share-task-web:latest

# Verify image was created
docker images | grep share-task-web
```

### Step 3.3: Setup Local Docker Registry

A local Docker registry allows you to store and manage images without using Docker Hub.

```bash
# Start Docker Registry container
docker run -d \
  --name local-registry \
  -p 5000:5000 \
  -v registry_data:/var/lib/registry \
  registry:2

# Verify registry is running
docker ps | grep local-registry

# Access registry at http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/_catalog
```

### Step 3.4: Push Image to Local Registry

```bash
# Push the image
docker push localhost:5000/share-task-web:latest

# Verify push (should return image digest)
curl http://localhost:5000/v2/share-task-web/tags/list

# Expected output:
# {"name":"share-task-web","tags":["latest"]}
```

### Step 3.5: Pull Image from Local Registry (for testing)

```bash
# First, remove local image to test pull
docker rmi localhost:5000/share-task-web:latest

# Pull from registry
docker pull localhost:5000/share-task-web:latest

# Run container from pulled image
docker run -p 8000:8000 localhost:5000/share-task-web:latest
```

### Step 3.6: Verify Docker Image

```bash
# List all images
docker images

# Inspect image details
docker inspect share-task-web:latest

# Run container and test
docker run -d -p 8000:8000 --name test-web share-task-web:latest
docker logs test-web

# Access app at http://localhost:8000
# Stop container
docker stop test-web
docker rm test-web
```

---

## Phase 4: Kubernetes Deployment

### Step 4.1: Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --memory=4096 --cpus=2

# Verify Minikube is running
minikube status

# Get Minikube info
kubectl cluster-info
kubectl get nodes
```

### Step 4.2: Configure Minikube to Use Local Registry

```bash
# Enable insecure registry (for local testing)
minikube ssh
docker run --rm -it --privileged --pid=host justincormack/nsenter1 \
  /bin/sh -c 'echo "{\"insecure-registries\": [\"host.docker.internal:5000\"]}" > /etc/docker/daemon.json'

# Or use this simpler approach
minikube ssh "sudo mkdir -p /etc/docker && \
  echo '{\"insecure-registries\": [\"localhost:5000\", \"host.docker.internal:5000\"]}' | \
  sudo tee /etc/docker/daemon.json"

minikube ssh "sudo systemctl restart docker"

# Verify configuration
minikube ssh "cat /etc/docker/daemon.json"
```

### Step 4.3: Build and Deploy Image into Minikube

```bash
# Option A: Use provided script (recommended)
cd /home/om/Desktop/Share-Task
./scripts/run-minikube.sh

# This script:
# 1. Starts Minikube
# 2. Builds image into Minikube
# 3. Applies all k8s manifests
# 4. Shows the service URL
```

### Step 4.4: Understand Kubernetes Manifests

Your `k8s/` folder contains several YAML files:

**1. Namespace & ConfigMap** (`00-namespace-configmap-secrets.yaml`):
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todolist
---
# ConfigMaps store non-sensitive configuration
kind: ConfigMap
metadata:
  name: app-config
  namespace: todolist
data:
  DATABASE_URL: "postgresql://user:pass@db:5432/todolist"
```

**2. Deployment** (`01-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todolist-app
  namespace: todolist
spec:
  replicas: 2  # Run 2 instances of the app
  selector:
    matchLabels:
      app: todolist-app
  template:
    metadata:
      labels:
        app: todolist-app
    spec:
      containers:
      - name: web
        image: share-task-web:latest
        ports:
        - containerPort: 8000
```

**3. Service** (`04-service-nodeport.yaml`):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todolist-service
  namespace: todolist
spec:
  type: NodePort
  selector:
    app: todolist-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    nodePort: 30080  # Accessible at http://minikube-ip:30080
```

### Step 4.5: Verify Deployment

```bash
# Check Minikube cluster
kubectl get all -n todolist

# Check pod status
kubectl get pods -n todolist
kubectl describe pod <pod-name> -n todolist

# Check deployment status
kubectl get deployment -n todolist
kubectl describe deployment todolist-app -n todolist

# Check service
kubectl get svc -n todolist

# View deployment logs
kubectl logs -n todolist -l app=todolist-app --tail=50

# Follow logs in real-time
kubectl logs -n todolist -l app=todolist-app -f
```

### Step 4.6: Access Application

```bash
# Get Minikube IP
minikube ip

# Get service URL (automatic)
minikube service todolist-service -n todolist --url

# Access application
open "http://$(minikube ip):30080"  # macOS
xdg-open "http://$(minikube ip):30080"  # Linux

# Or use port-forward
kubectl port-forward svc/todolist-service 8000:80 -n todolist
# Then open http://localhost:8000
```

### Step 4.7: Manual Kubernetes Commands (optional)

```bash
# Apply manifests manually
kubectl apply -f k8s/00-namespace-configmap-secrets.yaml
kubectl apply -f k8s/01-deployment.yaml
kubectl apply -f k8s/02-rbac-network-policy.yaml
kubectl apply -f k8s/03-ingress.yaml
kubectl apply -f k8s/04-service-nodeport.yaml

# Or apply all at once
kubectl apply -f k8s/

# Delete deployment
kubectl delete namespace todolist

# Scale deployment
kubectl scale deployment todolist-app --replicas=3 -n todolist

# Update image (for new builds)
kubectl set image deployment/todolist-app \
  web=localhost:5000/share-task-web:v2 -n todolist

# Rollout status
kubectl rollout status deployment/todolist-app -n todolist

# View rollout history
kubectl rollout history deployment/todolist-app -n todolist
```

---

## Phase 5: Monitoring (Prometheus + Grafana)

### Step 5.1: Setup Prometheus for Metrics Collection

#### Option A: Using Docker Compose (Simplest)

```bash
# Create prometheus.yml config
cat > /home/om/Desktop/Share-Task/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']
  
  - job_name: 'node'
    static_configs:
      - targets: ['host.docker.internal:9100']
EOF

# Start Prometheus container
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /home/om/Desktop/Share-Task/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml

# Access Prometheus at http://localhost:9090
```

#### Option B: Using Helm in Kubernetes (Advanced)

```bash
# Add Prometheus Helm chart repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Create monitoring namespace
kubectl create namespace monitoring

# Install Prometheus Stack
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.retention=7d \
  --set grafana.adminPassword=admin123
```

### Step 5.2: Setup Node Exporter (System Metrics)

```bash
# Install Node Exporter on host machine
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz
tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz
sudo mv node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/
sudo useradd --no-create-home --shell /bin/false node_exporter

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null << EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter

# Verify metrics at http://localhost:9100/metrics
curl http://localhost:9100/metrics | head -20
```

### Step 5.3: Setup cAdvisor (Container Metrics)

```bash
# Start cAdvisor container (for Docker container metrics)
docker run -d \
  --name cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  -p 8080:8080 \
  gcr.io/cadvisor/cadvisor:latest

# But cAdvisor uses port 8080, so let's use different port
docker run -d \
  --name cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  -p 8081:8080 \
  gcr.io/cadvisor/cadvisor:latest

# Access cAdvisor at http://localhost:8081

# Update prometheus.yml to include cAdvisor
cat >> /home/om/Desktop/Share-Task/prometheus.yml << 'EOF'
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['host.docker.internal:8081']
EOF

# Restart Prometheus
docker restart prometheus
```

### Step 5.4: Setup Grafana for Visualization

```bash
# Start Grafana container
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin123 \
  grafana/grafana:latest

# Access Grafana at http://localhost:3000
# Default credentials: admin / admin123
```

### Step 5.5: Configure Grafana Data Source

1. **Open Grafana**: Visit `http://localhost:3000`
2. **Login**: admin / admin123
3. **Add Data Source**:
   - Click gear icon (Settings) → Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - URL: `http://localhost:9090` (or `http://host.docker.internal:9090` if in container)
   - Click "Save & Test"
4. **Verify**: Should show "Data source is working"

### Step 5.6: Create Dashboards

#### Option A: Import Pre-built Dashboards

1. In Grafana, click **+** (Create) → **Import**
2. Use these popular dashboard IDs:
   - **1860**: Node Exporter Full
   - **11074**: NODE EXPORTER FOR PROMETHEUS DASHBOARD
   - **6417**: Docker and Host Monitoring

3. For each, enter the ID and click "Load"
4. Select Prometheus data source
5. Click "Import"

#### Option B: Create Custom Dashboard

1. Click **+** (Create) → **Dashboard**
2. Click **Add new panel**
3. Configure panel:
   - **Metrics**: Choose Prometheus metrics
   - **Visualization**: Graph, Stat, Gauge, etc.
4. Common queries:
   ```
   # CPU Usage
   rate(node_cpu_seconds_total[5m])
   
   # Memory Usage
   node_memory_MemAvailable_bytes
   
   # Disk Usage
   node_filesystem_avail_bytes
   
   # Container CPU
   rate(container_cpu_usage_seconds_total[5m])
   
   # Container Memory
   container_memory_usage_bytes
   ```
5. Click "Save"

### Step 5.7: Setup Alerts (Optional)

```bash
# You can configure alert rules in Prometheus
cat > /home/om/Desktop/Share-Task/alerts.yml << 'EOF'
groups:
  - name: app_alerts
    interval: 30s
    rules:
      - alert: HighCPUUsage
        expr: node_cpu_seconds_total > 0.8
        for: 5m
        annotations:
          summary: "High CPU usage detected"
      
      - alert: HighMemoryUsage
        expr: node_memory_MemAvailable_bytes < 500000000
        for: 5m
        annotations:
          summary: "High memory usage detected"
      
      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0.1
        for: 5m
        annotations:
          summary: "Pod is crash looping"
EOF

# Add to prometheus.yml
cat >> /home/om/Desktop/Share-Task/prometheus.yml << 'EOF'

rule_files:
  - '/etc/prometheus/alerts.yml'
EOF
```

---

## 📊 Complete Workflow

### Manual Step-by-Step Workflow

```bash
# ============================================
# 1. DEVELOPER: Make changes and push code
# ============================================
cd /home/om/Desktop/Share-Task
git checkout -b feature/new-feature
# ... edit files ...
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create PR on GitHub, get approval, merge to main
git checkout main
git pull origin main

# ============================================
# 2. JENKINS: Automatic trigger on push to main
# ============================================
# (Happens automatically if webhook is configured)
# OR manually trigger:
# - Go to Jenkins UI
# - Click "Build Now" on share-task-pipeline

# ============================================
# 3. DOCKER: Build image (via Jenkins)
# ============================================
# Jenkins runs commands in Jenkinsfile:
docker build -t share-task-web:latest -f todolist/Dockerfile .
docker tag share-task-web:latest localhost:5000/share-task-web:latest
docker push localhost:5000/share-task-web:latest

# ============================================
# 4. KUBERNETES: Deploy updated image
# ============================================
# Option A: Manual deployment
kubectl set image deployment/todolist-app \
  web=localhost:5000/share-task-web:latest \
  -n todolist

# Option B: Apply updated manifests
kubectl apply -f k8s/

# ============================================
# 5. VERIFICATION: Test the deployment
# ============================================
kubectl get pods -n todolist
kubectl logs -n todolist -l app=todolist-app
minikube service todolist-service -n todolist --url

# ============================================
# 6. MONITORING: Check dashboards
# ============================================
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
# View custom dashboards for application metrics
```

### Automated CI/CD Workflow

```bash
# ============================================
# Full Automated Setup (run once)
# ============================================

# 1. Start all services
minikube start --driver=docker --memory=4096
docker run -d --name local-registry -p 5000:5000 registry:2
docker run -d --name prometheus -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus:latest
docker run -d --name grafana -p 3000:3000 -e GF_SECURITY_ADMIN_PASSWORD=admin123 grafana/grafana:latest

# 2. Setup Jenkins webhook (one-time)
# GitHub Settings → Webhooks → Add https://yourdomain/github-webhook/

# 3. Deploy initial application
./scripts/run-minikube.sh

# 4. Monitor
# - Jenkins: http://localhost:8080
# - App: http://$(minikube ip):30080
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000

# ============================================
# Continuous Development
# ============================================

# Every time you push to main:
# 1. Jenkins automatically builds and tests
# 2. Docker image created and pushed to registry
# 3. Kubernetes deployment updated
# 4. Metrics collected in Prometheus
# 5. View in Grafana dashboard
```

---

## 🐛 Troubleshooting

### Minikube Issues

```bash
# Issue: Minikube won't start
# Solution 1: Clean restart
minikube delete
minikube start --driver=docker

# Solution 2: Check Docker
docker ps  # Ensure Docker is running

# Issue: Pods stuck in pending
kubectl get pods -n todolist -o wide
kubectl describe pod <pod-name> -n todolist  # Check events

# Issue: Image pull error
# Solution: Ensure image exists in Minikube
minikube image ls | grep share-task-web
minikube image build -t share-task-web:latest -f todolist/Dockerfile .
```

### Jenkins Issues

```bash
# Issue: Jenkins won't start
# Solution 1: Check if port 8080 is in use
sudo lsof -i :8080
Kill the process: sudo kill -9 <PID>

# Solution 2: Restart Jenkins
sudo systemctl restart jenkins

# Issue: Build fails in Jenkins
# Solution: Check console output
# Jenkins UI → Job → Build number → Console Output

# Issue: GitHub webhook not working
# Solution: Verify webhook in GitHub Settings
# Test delivery: Settings → Webhooks → Recent Deliveries → Redeliver
```

### Docker Issues

```bash
# Issue: Cannot push to local registry
# Solution: Ensure registry is running
docker ps | grep registry  # Must show running

# Issue: Image not found
# Solution: Rebuild image
docker build -t share-task-web:latest -f todolist/Dockerfile .

# Issue: Container port conflicts
# Solution: Use different ports
docker run -p 8001:8000 share-task-web:latest
```

### Prometheus/Grafana Issues

```bash
# Issue: No metrics in Prometheus
# Solution: Check targets
# Prometheus UI → Status → Targets
# Ensure all targets are "UP"

# Issue: Grafana can't connect to Prometheus
# Solution: Verify data source configuration
# Settings → Data Sources → Edit Prometheus
# URL should be http://prometheus:9090 (if containerized)

# Issue: Memory issues
# Solution: Limit container memory
docker run -m 512m prometheus:latest
```

### Application Issues

```bash
# Issue: Application returns 500 error
kubectl logs -n todolist -l app=todolist-app

# Solution 1: Database not initialized
kubectl exec -it <pod-name> -n todolist -- \
  python manage.py migrate

# Solution 2: Static files not collected
kubectl exec -it <pod-name> -n todolist -- \
  python manage.py collectstatic --noinput

# Issue: Application slow
# Solution: Check resource usage
kubectl top pods -n todolist
kubectl top nodes

# Solution: Scale deployment
kubectl scale deployment todolist-app --replicas=3 -n todolist
```

---

## 📚 Useful Commands Reference

### Git Commands
```bash
git status                    # See current branch and changes
git log --oneline            # View commit history
git diff                      # See uncommitted changes
git branch -a                # List all branches
git merge <branch>           # Merge branch to current branch
git reset --hard HEAD        # Discard all changes (WARNING!)
```

### Docker Commands
```bash
docker ps                    # List running containers
docker ps -a                 # List all containers
docker images                # List images
docker build -t name:tag .   # Build image
docker run -d -p 8000:8000 image  # Run container
docker logs <container>      # View container logs
docker exec -it <container> bash  # Access container shell
docker stop <container>      # Stop container
docker rm <container>        # Delete container
docker rmi <image>           # Delete image
```

### Kubernetes Commands
```bash
kubectl get pods -n <namespace>          # List pods
kubectl get services -n <namespace>      # List services
kubectl get deployments -n <namespace>   # List deployments
kubectl describe pod <pod> -n <namespace>  # Pod details
kubectl logs <pod> -n <namespace>        # Pod logs
kubectl exec -it <pod> -n <namespace> bash  # Access pod
kubectl apply -f file.yaml               # Apply manifest
kubectl delete -f file.yaml              # Delete resources
kubectl scale deployment <name> --replicas=3  # Scale pods
```

### Prometheus Query Examples
```
node_cpu_seconds_total          # CPU usage
node_memory_MemAvailable_bytes  # Available memory
node_disk_io_now                # Disk I/O
container_memory_usage_bytes    # Container memory
rate(container_cpu_usage_seconds_total[5m])  # Container CPU rate
```

---

## ✅ Validation Checklist

Before considering the deployment complete, verify:

- [ ] GitHub repository created and code pushed
- [ ] Jenkins job created and triggered successfully
- [ ] Docker image built and pushed to local registry
- [ ] Minikube cluster running with 2 pods
- [ ] Application accessible at `http://minikube-ip:30080`
- [ ] Prometheus collecting metrics (check Status → Targets)
- [ ] Grafana dashboards displaying metrics
- [ ] Logs showing in Grafana and Kubernetes
- [ ] Can scale deployment: `kubectl scale deployment todolist-app --replicas=3 -n todolist`
- [ ] Rolling update works: Change image and watch pods update
- [ ] Alerts trigger when CPU/Memory exceeds threshold (if configured)

---

## 🎯 Next Steps

1. **Development**: Make code changes locally
2. **Testing**: Run `python todolist/manage.py test` locally before pushing
3. **Push**: `git push origin main` → Jenkins autobuilds
4. **Monitor**: Check Grafana for metrics and health
5. **Scale**: Increase replicas if needed: `kubectl scale deployment todolist-app --replicas=5 -n todolist`
6. **Update**: For new versions, rebuild and deploy same way

---

## 📞 Quick Support

### Common Questions

**Q: How do I update the application?**
A: Push code to GitHub → Jenkins builds automatically → Kubernetes updates pods

**Q: How do I check if deployment is healthy?**
A: `kubectl get pods -n todolist` (should show RUNNING) and `kubectl logs -n todolist -l app=todolist-app`

**Q: How do I scale the application?**
A: `kubectl scale deployment todolist-app --replicas=5 -n todolist`

**Q: How do I view application metrics?**
A: Open Grafana (http://localhost:3000) and view custom dashboards

**Q: How do I rollback to previous version?**
A: `kubectl rollout undo deployment/todolist-app -n todolist`

---

## 📖 Additional Resources

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Git Documentation](https://git-scm.com/doc)

---

**Last Updated**: February 21, 2026
**Version**: 1.0
**Status**: Ready for deployment

Good luck with your deployment! 🚀
