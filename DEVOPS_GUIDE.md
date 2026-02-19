# DevOps Deployment Guide for Share-Task

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development](#local-development)
4. [AWS Deployment](#aws-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The Share-Task application follows a modern DevOps architecture with multiple deployment options:

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub Repository                    │
│         (Code + Infrastructure as Code)                  │
└─────────────┬───────────────────────────────────────────┘
              │
              ├─► GitHub Actions (CI/CD)
              │
              ├─► Jenkins Pipeline
              │
              └─► Manual Deployment
                      │
        ┌─────────────┼─────────────┐
        │             │             │
    ┌───▼───┐     ┌───▼───┐   ┌───▼───┐
    │ Docker│     │Ansible│   │Terraform│
    │ Build │     │Config │   │Infra    │
    └───┬───┘     └───────┘   └────┬────┘
        │                          │
    ┌───▼──────────────────────────▼────┐
    │      AWS ECR (Container Registry)   │
    └───┬──────────────────────────────┬─┘
        │                              │
    ┌───▼──────────────┐         ┌────▼──────────┐
    │  AWS ECS/Fargate │         │  Kubernetes   │
    │  + ALB + RDS     │         │  (EKS/Self)   │
    │  + Redis         │         │  + Ingress    │
    └────┬─────────────┘         └────┬──────────┘
         │                            │
         └────────────┬───────────────┘
                      │
              ┌───────▼────────┐
              │  Domain (DNS)  │
              │  yourdomain.com │
              └────────────────┘
```

### Components:
- **Frontend**: Served via Nginx (reverse proxy, SSL termination)
- **Backend**: Django + DRF (Python)
- **Database**: PostgreSQL (RDS)
- **Cache**: Redis (ElastiCache/Standalone)
- **Container Registry**: AWS ECR
- **Orchestration**: ECS Fargate or Kubernetes
- **Load Balancer**: AWS ALB (ECS) or Ingress (K8s)
- **DNS**: Route53 or external DNS provider

---

## Prerequisites

### Required Tools:
```bash
# AWS CLI
aws --version  # >= 2.0

# Docker
docker --version  # >= 20.0

# Docker Compose
docker-compose --version  # >= 1.29.0

# Terraform
terraform --version  # >= 1.0

# kubectl (for Kubernetes)
kubectl version --client  # >= 1.24

# Ansible (for automation)
ansible --version  # >= 2.9

# Git
git --version
```

### AWS Prerequisites:
1. AWS Account with appropriate permissions
2. AWS Access Keys configured: `aws configure`
3. EC2 Key Pair created
4. Domain name registered (Route53 or external)
5. SSL Certificate created in ACM

### Environment Variables:
```bash
# Copy and customize the template
cp .env.example .env

# Generate a strong SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## Local Development

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/Share-Task.git
cd Share-Task

# Create environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python todolist/manage.py migrate

# Create superuser
docker-compose exec web python todolist/manage.py createsuperuser

# Collect static files
docker-compose exec web python todolist/manage.py collectstatic --noinput

# Access the application
# - Django: http://localhost:8000
# - Nginx: http://localhost
# - Admin: http://localhost/admin
```

### Option 2: Local Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r todolist/requirements.txt

# Setup database (make sure PostgreSQL is running)
python todolist/manage.py migrate

# Create superuser
python todolist/manage.py createsuperuser

# Start development server
python todolist/manage.py runserver

# In another terminal, start Celery (if needed)
celery -A todolist worker -l info
```

---

## AWS Deployment

### Step 1: Prepare AWS Account

```bash
# Configure AWS CLI
aws configure

# Create S3 bucket for Terraform state
aws s3 mb s3://share-task-terraform-state-$(date +%s) --region us-east-1

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1
```

### Step 2: Setup SSL Certificate

```bash
# Create SSL certificate in AWS ACM
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names www.yourdomain.com \
  --validation-method DNS \
  --region us-east-1

# Note the Certificate ARN
# Verify domain in Route53 when prompted
```

### Step 3: Deploy with Terraform

```bash
# Navigate to terraform directory
cd terraform

# Copy and customize variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values:
# - domain_name: yourdomain.com
# - certificate_arn: arn:aws:acm:...
# - docker_image_url: your-account-id.dkr.ecr.us-east-1.amazonaws.com/share-task-repo:latest

# Initialize Terraform
terraform init \
  -backend-config="bucket=share-task-terraform-state-xxx" \
  -backend-config="key=prod/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=terraform-locks"

# Plan the infrastructure
terraform plan -out=tfplan

# Review and approve
terraform apply tfplan

# Save outputs
terraform output > ../deployment-outputs.txt
```

### Step 4: Build and Push Docker Image

```bash
# Navigate to project root
cd ..

# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t share-task:latest .

# Tag for ECR
docker tag share-task:latest \
  your-account-id.dkr.ecr.us-east-1.amazonaws.com/share-task-repo:latest

# Push to ECR
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/share-task-repo:latest
```

### Step 5: Deploy to ECS

```bash
# Update ECS service with new image
aws ecs update-service \
  --cluster share-task-cluster \
  --service share-task-service \
  --force-new-deployment \
  --region us-east-1

# Wait for deployment to complete
aws ecs wait services-stable \
  --cluster share-task-cluster \
  --services share-task-service \
  --region us-east-1

# Get ALB DNS name
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[?LoadBalancerName==`share-task-alb`].DNSName' \
  --output text
```

### Step 6: Configure DNS

```bash
# Get Route53 nameservers
aws route53 get-hosted-zone \
  --id /hostedzone/YOUR_ZONE_ID \
  --query 'DelegationSet.NameServers' \
  --output table

# Update your domain registrar with these nameservers
```

---

## Kubernetes Deployment

### Option 1: AWS EKS

```bash
# Create EKS cluster using terraform (already defined)
# See terraform/ directory for EKS configuration

# Configure kubectl
aws eks update-kubeconfig \
  --name share-task-cluster \
  --region us-east-1

# Verify connection
kubectl cluster-info
```

### Option 2: Self-Managed Kubernetes

```bash
# Install prerequisites
sudo apt-get update && apt-get install -y \
  curl \
  gnupg \
  lsb-release

# Add Kubernetes repository (Ubuntu/Debian)
curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg \
  https://packages.cloud.google.com/apt/doc/apt-key.gpg

echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install kubeadm, kubelet, kubectl
sudo apt-get update
sudo apt-get install -y kubeadm kubelet kubectl

# Initialize master node (on master)
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Setup kubeconfig
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install CNI (Flannel)
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

# Join worker nodes (on workers)
# Use the command provided by kubeadm init
```

### Step 2: Deploy Application

```bash
# Update image URL in manifests
sed -i 's|your-account-id.dkr.ecr|YOUR_ACTUAL_ID.dkr.ecr|g' k8s/*.yaml

# Create namespace and deploy
kubectl apply -f k8s/00-namespace-configmap-secrets.yaml
kubectl apply -f k8s/01-deployment.yaml
kubectl apply -f k8s/02-rbac-network-policy.yaml
kubectl apply -f k8s/03-ingress.yaml

# Verify deployment
kubectl get pods -n todolist
kubectl get svc -n todolist
kubectl get ingress -n todolist

# Check logs
kubectl logs -n todolist deployment/todolist-app -f
```

### Step 3: Setup Ingress Controller (if not using AWS ALB)

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml

# Install Cert Manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Verify installation
kubectl get pods -n ingress-nginx
kubectl get pods -n cert-manager
```

### Step 4: Update DNS for Ingress

```bash
# Get Ingress IP
kubectl get ingress -n todolist

# Create DNS A record pointing to Ingress IP
# Or if using AWS NLB with Ingress:
kubectl get svc -n ingress-nginx -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}'
```

---

## CI/CD Pipeline

### GitHub Actions Setup

```bash
# Add secrets to GitHub repository
# Settings > Secrets and variables > Actions

# Required secrets:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_ACCOUNT_ID
# - KUBECONFIG (base64 encoded)
# - DOCKER_REGISTRY_TOKEN (if using private registry)
```

### Jenkins Setup

```bash
# Run Ansible playbook to install Jenkins
cd ansible

ansible-playbook \
  -i inventory.ini \
  -e "aws_access_key_id=YOUR_KEY" \
  -e "aws_secret_access_key=YOUR_SECRET" \
  jenkins-setup.yml

# Access Jenkins
# http://jenkins-server-ip:8080

# Get initial admin password
cat /var/lib/jenkins/secrets/initialAdminPassword
```

### Manual Pipeline Trigger

```bash
# Webhook URL for Jenkins
# https://jenkins.yourdomain.com/github-webhook/

# For GitHub Actions: Commits to main branch automatically trigger pipeline

# Manual deployment
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/yourusername/Share-Task/actions/workflows/ci-cd.yml/dispatches \
  -d '{"ref":"main"}'
```

---

## Security Considerations

### SSL/TLS Configuration

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Place in ssl/ directory
mkdir -p ssl
cp cert.pem key.pem ssl/

# For production, use AWS ACM or Let's Encrypt
```

### Secrets Management

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name todolist/django-secret-key \
  --secret-string "your-secret-key"

# Rotate secrets regularly
aws secretsmanager rotate-secret \
  --secret-id todolist/django-secret-key
```

### IAM Permissions (Principle of Least Privilege)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService",
        "ecs:DescribeServices"
      ],
      "Resource": "arn:aws:ecs:region:account-id:service/share-task-cluster/share-task-service"
    }
  ]
}
```

### Network Security

```bash
# Security Groups are configured in Terraform
# Review: terraform/security_groups.tf

# Key points:
# - ALB accessible only on ports 80/443
# - ECS tasks accessible only from ALB
# - RDS accessible only from ECS
# - Redis accessible only from ECS
```

### Data Encryption

- RDS encryption enabled by default
- SSL/TLS for all external communication
- Django SECRET_KEY stored in AWS Secrets Manager
- Environment variables encrypted in ECS task definitions

---

## Monitoring & Logging

### CloudWatch

```bash
# View ECS logs
aws logs tail /ecs/share-task --follow

# Create custom metric
aws cloudwatch put-metric-data \
  --namespace Share-Task \
  --metric-name ActiveUsers \
  --value 100
```

### Application Health

```bash
# Health check endpoint
curl http://localhost:8000/health/

# Check ECS task health
aws ecs describe-services \
  --cluster share-task-cluster \
  --services share-task-service \
  --query 'services[0].deployments'
```

---

## Troubleshooting

### ECS Deployment Issues

```bash
# Check service events
aws ecs describe-services \
  --cluster share-task-cluster \
  --services share-task-service \
  --query 'services[0].events' \
  --output table

# Check task logs
aws logs tail /ecs/share-task --follow

# Restart service
aws ecs update-service \
  --cluster share-task-cluster \
  --service share-task-service \
  --force-new-deployment
```

### Kubernetes Debugging

```bash
# Check pod status
kubectl describe pod <pod-name> -n todolist

# Check logs
kubectl logs <pod-name> -n todolist -c todolist

# Shell into container
kubectl exec -it <pod-name> -n todolist -- /bin/bash

# Check ingress status
kubectl describe ingress todolist-ingress -n todolist
```

### Database Connection Issues

```bash
# Test RDS connection
psql -h <rds-endpoint> -U admin -d todolist_db

# Check security groups
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=share-task-rds-sg"

# Verify RDS status
aws rds describe-db-instances \
  --db-instance-identifier share-task-db
```

### Docker Image Issues

```bash
# Build with verbose output
docker build -t share-task:latest . --progress=plain

# Run container locally
docker run -it --rm \
  -e DEBUG=False \
  -e SECRET_KEY=test \
  share-task:latest

# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image share-task:latest
```

---

## Scaling & Performance

### Auto-Scaling Configuration

**ECS:**
- CPU Utilization > 70% → Scale Up
- Memory Utilization > 80% → Scale Up
- Min: 2 tasks, Max: 4 tasks

**Kubernetes:**
- CPU request: 250m, limit: 500m
- Memory request: 512Mi, limit: 1024Mi
- HPA: 2-5 replicas

### Performance Optimization

```bash
# Enable gzip compression (nginx.conf already configured)
# Cache static files (30 days)
# Use CDN for media files
# Enable query caching in Django ORM

# Monitor performance
# Use Django Debug Toolbar (development only)
# Setup APM with New Relic or DataDog
```

---

## Cost Optimization

- Use Fargate Spot instances (70% cheaper)
- Reserved Instances for predictable workloads
- S3 Lifecycle policies for old backups
- CloudWatch log retention: 30 days
- Delete unused snapshots and AMIs

---

## Support & Documentation

- Django Docs: https://docs.djangoproject.com/
- AWS ECS: https://docs.aws.amazon.com/ecs/
- Kubernetes: https://kubernetes.io/docs/
- Terraform: https://www.terraform.io/docs/
- Docker: https://docs.docker.com/

---

## Next Steps

1. **Setup Domain**: Purchase and configure your domain
2. **Generate SSL Cert**: Request certificate in AWS ACM
3. **Configure Terraform**: Update tfvars with your details
4. **Deploy Infrastructure**: `terraform apply`
5. **Build & Push Image**: Docker build and push to ECR
6. **Deploy Application**: Update ECS/K8s with image
7. **Configure DNS**: Update Route53/DNS records
8. **Enable Monitoring**: Setup CloudWatch alarms
9. **Test Application**: Verify functionality
10. **Setup CI/CD**: Configure GitHub Actions/Jenkins

---

**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Version**: 1.0
