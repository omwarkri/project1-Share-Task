# Quick Start Guide - Share-Task DevOps Deployment

## 🚀 5-Minute Setup (Local Development)

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/Share-Task.git
cd Share-Task

# 2. Setup environment
cp .env.example .env

# 3. Start everything with Docker Compose
docker-compose up -d

# 4. Initialize database
docker-compose exec web python todolist/manage.py migrate
docker-compose exec web python todolist/manage.py createsuperuser
docker-compose exec web python todolist/manage.py collectstatic --noinput

# 5. Access the app
# - Main app: http://localhost
# - Admin: http://localhost/admin
```

## 📦 Key Files Created

### Docker & Containers
- **[Dockerfile](Dockerfile)** - Multi-stage Docker build for production
- **[docker-compose.yml](docker-compose.yml)** - Full stack with DB, Redis, Celery
- **[.dockerignore](.dockerignore)** - Optimized Docker build context
- **[nginx.conf](nginx.conf)** - Production-grade Nginx configuration

### Infrastructure as Code
- **[terraform/main.tf](terraform/main.tf)** - Provider and backend config
- **[terraform/vpc.tf](terraform/vpc.tf)** - VPC, subnets, NAT gateways
- **[terraform/security_groups.tf](terraform/security_groups.tf)** - Network security
- **[terraform/rds_redis.tf](terraform/rds_redis.tf)** - Database and cache
- **[terraform/ecs.tf](terraform/ecs.tf)** - ECS cluster and auto-scaling
- **[terraform/alb.tf](terraform/alb.tf)** - Load balancer and DNS
- **[terraform/ecr.tf](terraform/ecr.tf)** - Container registry
- **[terraform/secrets.tf](terraform/secrets.tf)** - Secrets management

### Kubernetes
- **[k8s/00-namespace-configmap-secrets.yaml](k8s/00-namespace-configmap-secrets.yaml)** - K8s namespace, configs, secrets
- **[k8s/01-deployment.yaml](k8s/01-deployment.yaml)** - Deployment with autoscaling
- **[k8s/02-rbac-network-policy.yaml](k8s/02-rbac-network-policy.yaml)** - RBAC and security policies
- **[k8s/03-ingress.yaml](k8s/03-ingress.yaml)** - Ingress with SSL

### CI/CD & Automation
- **[Jenkinsfile](Jenkinsfile)** - Jenkins pipeline definition
- **[.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)** - GitHub Actions workflow
- **[ansible/jenkins-setup.yml](ansible/jenkins-setup.yml)** - Jenkins installation
- **[ansible/docker-setup.yml](ansible/docker-setup.yml)** - Docker installation

### Configuration & Documentation
- **[.env.example](.env.example)** - Environment variables template
- **[DEVOPS_GUIDE.md](DEVOPS_GUIDE.md)** - Complete deployment guide
- **[terraform/terraform.tfvars.example](terraform/terraform.tfvars.example)** - Terraform variables template

## 📊 Architecture

```
GitHub → CI/CD Pipeline → ECR → ECS/K8s Cluster → ALB/Ingress → Domain
                ↓
           Testing & Security Scans
```

## 🔑 Key Features

✅ **Production-Ready Docker Setup**
- Multi-stage build for minimal image size
- Health checks configured
- Non-root user for security

✅ **Complete Infrastructure as Code**
- VPC with public/private subnets
- RDS PostgreSQL with Multi-AZ
- Redis ElastiCache cluster
- ECS Fargate with auto-scaling (2-4 tasks)
- Application Load Balancer
- Route53 DNS management

✅ **Kubernetes Support**
- Deployment with rolling updates
- Horizontal Pod Autoscaler (2-5 replicas)
- Network policies for security
- RBAC configuration
- SSL/TLS with cert-manager

✅ **Automated CI/CD**
- GitHub Actions (test, build, push, deploy)
- Jenkins pipeline (alternative)
- Security scanning (Trivy)
- Automated deployment to ECS or K8s

✅ **Security**
- Environment encryption
- AWS Secrets Manager integration
- Network policies and security groups
- SSL/TLS termination
- DDoS protection via ALB

✅ **Monitoring & Logging**
- CloudWatch logs integration
- Container health checks
- Pod disruption budgets
- Auto-scaling triggers

## 🚀 Deployment Commands

### AWS ECS Deployment
```bash
cd terraform
terraform init
terraform plan
terraform apply

# Build and push image
docker build -t yourdomain.com:latest .
aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_ECR_URL
docker push YOUR_ECR_URL/share-task-repo:latest

# Update service
aws ecs update-service --cluster share-task-cluster --service share-task-service --force-new-deployment
```

### Kubernetes Deployment
```bash
# Update images in k8s manifests
sed -i 's|YOUR_ECR_URL|actual-url|g' k8s/*.yaml

# Deploy
kubectl apply -f k8s/

# Monitor
kubectl get pods -n todolist
kubectl logs -n todolist deployment/todolist-app -f
```

## 📚 Documentation
- See [DEVOPS_GUIDE.md](DEVOPS_GUIDE.md) for detailed instructions

## 🔧 Quick Troubleshooting

**Container won't start?**
```bash
docker logs todolist-web
# Check .env file values
```

**Database connection error?**
```bash
docker-compose exec web python todolist/manage.py dbshell
# Check if migrations ran
```

**Port already in use?**
```bash
docker-compose down
# or change ports in docker-compose.yml
```

## 📞 Support
- Django: https://docs.djangoproject.com/
- Docker: https://docs.docker.com/
- AWS: https://docs.aws.amazon.com/
- Kubernetes: https://kubernetes.io/docs/

---

**Next**: Read [DEVOPS_GUIDE.md](DEVOPS_GUIDE.md) for production deployment instructions.
