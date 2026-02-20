# Quick Command Reference - Share-Task

## 🚀 START HERE - Choose Your Path

### Path 1: Local Python (Fastest - 5 min)
```bash
# One-time setup
python3 -m venv venv
source venv/bin/activate
pip install -r todolist/requirements.txt

# Navigate to app
cd todolist

# Run migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# Run server
python manage.py runserver

# Open browser to http://localhost:8000
```

### Path 2: Docker Compose (Full Stack - 10 min)
```bash
# Just one command!
docker-compose up -d

# Then setup (once only)
docker-compose exec web python todolist/manage.py migrate
docker-compose exec web python todolist/manage.py createsuperuser

# Open browser to http://localhost:3000
```

### Path 3: AWS ECS (Production - 45 min)
```bash
# Configure AWS
aws configure

# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# Build and push image
cd ..
docker build -t share-task . && docker push ...

# ECS auto-deploys new image
```

---

## 📋 Docker Compose Commands

```bash
# START/STOP
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose down -v        # Stop + delete volumes (!!!resets DB)
docker-compose restart        # Restart all services

# LOGS & DEBUGGING
docker-compose logs -f web    # Follow Django logs
docker-compose logs -f db     # Follow Database logs
docker-compose logs -f redis  # Follow Cache logs
docker-compose logs           # Show all logs (past)

# DATABASE
docker-compose exec web python todolist/manage.py migrate
docker-compose exec web python todolist/manage.py createsuperuser
docker-compose exec web python todolist/manage.py shell
docker-compose exec db psql -U postgres -d todolist_db

# STATIC FILES & ADMIN
docker-compose exec web python todolist/manage.py collectstatic --noinput

# CONTAINERS
docker-compose ps             # List all services
docker-compose exec web bash  # Shell into web container

# BUILD
docker-compose build          # Rebuild images if Dockerfile changed
docker-compose build --no-cache web  # Full rebuild
```

---

## 🐍 Django Commands (After cd todois/)

```bash
# DATABASE
python manage.py migrate              # Apply migrations
python manage.py makemigrations       # Create new migrations
python manage.py showmigrations       # Show migration history

# USER MANAGEMENT
python manage.py createsuperuser      # Create admin user
python manage.py changepassword       # Change password

# STATIC FILES
python manage.py collectstatic        # Collect static files
python manage.py collectstatic --noinput  # Non-interactive

# DATABASE UTILITIES
python manage.py dumpdata > backup.json   # Backup data
python manage.py loaddata backup.json     # Restore data

# SHELL & DEBUG
python manage.py shell               # Interactive Python shell
python manage.py dbshell             # Direct database shell

# DEVELOPMENT
python manage.py runserver           # Start dev server
python manage.py runserver 0.0.0.0:3000  # Custom host:port

# TESTING
python manage.py test                # Run all tests
python manage.py test app_name       # Test specific app

# FIXES
python manage.py check               # Check for errors
python manage.py systemcheck         # System requirements check
```

---

## 🏗️ Terraform Commands

```bash
cd terraform

# INITIALIZATION
terraform init              # Initialize Terraform (first time)

# PLANNING
terraform plan              # Show what will be created
terraform plan -out=tfplan  # Save plan to file

# DEPLOYMENT
terraform apply tfplan      # Create resources

# CLEANUP
terraform destroy           # Delete all resources (be careful!)
terraform destroy -auto-approve  # Automatic (no confirmation)

# INFORMATION
terraform state list        # List all resources
terraform output            # Show outputs (ALB URL, RDS endpoint, etc.)
terraform show              # Show full state
```

---

## 🐳 Docker Commands

```bash
# BUILD
docker build -t share-task:latest .           # Build image
docker build -t share-task:v1.0 .             # Build with version tag

# TAG
docker tag share-task:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/share-task:latest

# PUSH TO ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/share-task:latest

# IMAGES & CONTAINERS
docker images               # List images
docker ps                   # List running containers
docker ps -a                # List all containers

# CLEANUP
docker image rm share-task  # Delete image
docker container rm <ID>    # Delete container
docker prune                # Clean up unused images/containers
```

---

## ☁️ AWS CLI Commands

```bash
# AUTHENTICATION
aws configure               # Setup credentials
aws sts get-caller-identity # Verify credentials

# ECR (Container Registry)
aws ecr describe-repositories
aws ecr get-login-password --region us-east-1

# ECS (Container Service)
aws ecs list-clusters
aws ecs describe-services --cluster share-task-cluster --services share-task-service
aws ecs list-tasks --cluster share-task-cluster
aws ecs update-service --cluster share-task-cluster --service share-task-service \
  --force-new-deployment

# LOGS
aws logs tail /ecs/share-task-app --follow
aws logs tail /ecs/share-task-app --since 1h

# RDS (Database)
aws rds describe-db-instances --region us-east-1

# S3 (Storage)
aws s3 ls
aws s3 cp file.txt s3://bucket-name/
```

---

## 🔧 Jenkins & Ansible

### Ansible Commands

```bash
cd ansible

# DRY RUN (see what would happen)
ansible-playbook -i inventory.ini docker-setup.yml --check

# RUN PLAYBOOK
ansible-playbook -i inventory.ini docker-setup.yml
ansible-playbook -i inventory.ini jenkins-setup.yml

# PING HOSTS
ansible all -i inventory.ini -m ping

# RUN COMMAND
ansible all -i inventory.ini -m shell -a "docker --version"
```

### Jenkins Web Interface

- **Jenkins URL**: http://EC2_IP:8080
- **Create Job**: New Item → Pipeline
- **Run Job**: Build Now
- **View Logs**: Build number → Console Output
- **Configure Credentials**: Manage Jenkins → Manage Credentials

---

## 📦 Environment Files Location

```
Share-Task/
├── .env                          # Main environment (copy from .env.example)
├── terraform/terraform.tfvars    # AWS/Terraform config
├── ansible/inventory.ini         # Ansible hosts config
├── docker-compose.yml            # Docker Compose services
├── Jenkinsfile                   # Jenkins pipeline definition
└── todolist/
    └── todolist/settings.py      # Django settings
```

---

## 🗂️ Key Files Structure

```
Share-Task/
├── todolist/                     # Main Django app
│   ├── manage.py                # Django CLI
│   ├── requirements.txt          # Python dependencies
│   ├── todolist/settings.py      # Django config
│   ├── ai_task_management/       # Task app
│   ├── chat/                     # Chat app
│   ├── user/                     # User app
│   ├── task/                     # Task management
│   └── templates/                # HTML templates
│
├── k8s/                          # Kubernetes files (optional)
│   ├── 00-namespace-configmap-secrets.yaml
│   ├── 01-deployment.yaml
│   └── 03-ingress.yaml
│
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                   # Terraform config
│   ├── vpc.tf                    # Network setup
│   ├── ecs.tf                    # ECS configuration
│   ├── rds_redis.tf              # Database & cache
│   └── variables.tf              # Variable definitions
│
├── ansible/                      # Automation playbooks
│   ├── docker-setup.yml          # Docker installation
│   ├── jenkins-setup.yml         # Jenkins installation
│   └── inventory.ini             # Host configuration
│
├── Dockerfile                    # Docker build instructions
├── docker-compose.yml            # Multi-container setup
├── Jenkinsfile                   # CI/CD pipeline
├── nginx.conf                    # Web server config
└── .env.example                  # Environment template
```

---

## 🆘 Quick Troubleshooting

### Can't connect to Docker daemon?
```bash
# Start Docker service (Linux)
sudo systemctl start docker

# Or restart Docker Desktop (Mac/Windows)
```

### Port already in use?
```bash
# Find process using port
lsof -i :8000
# Kill it
kill -9 <PID>

# Or use different port
docker-compose -p service up -d  # Changes port
```

### Database error in Docker?
```bash
# Reset database volume
docker-compose down -v
docker-compose up -d
docker-compose exec web python todolist/manage.py migrate
```

### Permission denied on .pem file?
```bash
chmod 400 share-task-key.pem
```

### Jenkins won't start?
```bash
sudo systemctl restart jenkins
sudo tail -f /var/log/jenkins/jenkins.log  # View logs
```

---

## 📊 Service Health Check

```bash
# Is web app running?
curl http://localhost:8000/

# Is database connected?
docker-compose exec web python -c "import psycopg2; print('Database OK')"

# Is Redis working?
docker-compose exec redis redis-cli ping

# All services up?
docker-compose ps

# AWS ECS service healthy?
aws ecs describe-services --cluster share-task-cluster \
  --services share-task-service --query 'services[0].status'
```

---

## 🎯 Typical Development Workflow

```bash
# 1. Start Docker Compose (once per session)
docker-compose up -d

# 2. Work on code
# Edit files in your editor

# 3. Restart services if needed
docker-compose restart web

# 4. Check logs for errors
docker-compose logs -f web

# 5. Make database changes
docker-compose exec web python todolist/manage.py makemigrations
docker-compose exec web python todolist/manage.py migrate

# 6. When done for the day
docker-compose down

# 7. Push to GitHub
git add .
git commit -m "Feature: description"
git push origin main
# Jenkins auto-deploys to production!
```

---

## 📱 Access Points

| Component | URL | Purpose |
|-----------|-----|---------|
| Main App | http://localhost:3000 | Production setup |
| Direct Django | http://localhost:8000 | Dev setup |
| Admin Panel | http://localhost:3000/admin | Database UI |
| Database | localhost:5432 | PostgreSQL connection |
| Cache | localhost:6379 | Redis connection |
| Jenkins | http://EC2_IP:8080 | CI/CD pipeline |
| Prod (AWS) | ALB DNS from Terraform | Live app |

---

**Total Setup Time:**
- ⚡ Local Python: 5 minutes
- 🐳 Docker Compose: 10 minutes
- ☁️ AWS ECS: 45-60 minutes
- 🔄 Jenkins (with Ansible): 20 minutes

Start with local or Docker Compose, then move to AWS when ready! 🚀
