# 🚀 Complete Share-Task Application Run Guide

## 📌 Quick Overview

**Share-Task** is a Django-based team collaboration app. You can run it in **3 ways**:
1. **Local Development** (fastest - 5 minutes)
2. **Docker Compose** (production-like local setup)
3. **AWS ECS** (cloud production deployment)

---

## Part 1: Local Development Setup (Fastest)

### Prerequisites
```bash
# Install Python 3.11+
python3 --version

# Install pip (package manager)
pip3 --version

# Install Git
git --version
```

### Step-by-Step:

**Step 1: Clone and Navigate**
```bash
git clone https://github.com/your-username/Share-Task.git
cd Share-Task
```

**Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

**Step 3: Install Dependencies**
```bash
pip install -r todolist/requirements.txt
```

**Step 4: Setup Environment Variables**
```bash
# Copy example file
cp .env.example .env

# Edit .env if needed (for local dev, defaults are usually fine)
```

**Step 5: Setup Database**
```bash
cd todolist

# Run migrations (creates database tables)
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Follow prompts to create admin account

# Collect static files (CSS, JS)
python manage.py collectstatic --noinput

cd ..
```

**Step 6: Run Application**
```bash
cd todolist
python manage.py runserver
```

**Step 7: Access Application**
- **Main App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Login**: Use credentials you created in Step 5

✅ **That's it! Your app is running locally!**

---

## Part 2: Docker Compose Setup (Production-Like Local)

### Why Docker Compose?
- Includes database, cache, background jobs
- Same setup as production
- Easier to test real features

### Prerequisites
```bash
# Install Docker
docker --version  # >= 20.0

# Install Docker Compose
docker-compose --version  # >= 1.29.0
```

### Step-by-Step:

**Step 1: Clone Repository**
```bash
git clone https://github.com/your-username/Share-Task.git
cd Share-Task
```

**Step 2: Create Environment File**
```bash
cp .env.example .env
# Defaults are already configured for Docker Compose
```

**Step 3: Start All Services**
```bash
docker-compose up -d
```

**This starts:**
- PostgreSQL Database
- Redis Cache
- Django Web App
- Celery Worker (background jobs)
- Celery Beat (scheduler)
- Nginx Reverse Proxy

**Step 4: Initialize Database**
```bash
# Run migrations
docker-compose exec web python todolist/manage.py migrate

# Create superuser
docker-compose exec web python todolist/manage.py createsuperuser

# Collect static files
docker-compose exec web python todolist/manage.py collectstatic --noinput
```

**Step 5: Access Application**
- **Main App**: http://localhost:3000 (Nginx Proxy)
- **Direct Django**: http://localhost:8000
- **Admin Panel**: http://localhost:3000/admin
- **Database**: postgres://postgres:postgres@localhost:5432/todolist_db
- **Redis Cache**: localhost:6379

### Useful Docker Compose Commands

```bash
# View status of all containers
docker-compose ps

# View logs of specific service
docker-compose logs -f web      # Follow Django logs
docker-compose logs -f db       # Follow Database logs
docker-compose logs -f celery   # Follow Background jobs

# Stop all services
docker-compose down

# Stop and remove volumes (cleans database)
docker-compose down -v

# Restart a specific service
docker-compose restart web

# Access Django shell
docker-compose exec web python todolist/manage.py shell

# Run Django management command
docker-compose exec web python todolist/manage.py <command>
```

✅ **Docker Compose Setup Complete!**

---

## Part 3: AWS ECS Deployment (Production)

### Architecture Explanation

```
┌─────────────────┐
│    Git Push     │
│   (Main branch) │
└────────┬────────┘
         │
         └──► Jenkins/GitHub Actions Pipeline
              │
              ├─ Code Checkout
              ├─ Run Tests
              ├─ Build Docker Image
              ├─ Security Scans
              ├─ Push to AWS ECR (Image Registry)
              │
              └──► AWS ECS (Container Orchestration)
                   ├─ Load Balancer (ALB)
                   ├─ Application Instances (Auto-scaling 2-4)
                   ├─ PostgreSQL RDS (Database)
                   ├─ Redis ElastiCache (Cache)
                   └─ CloudWatch (Monitoring)
                   
                   ↓ Accessible via
                   Domain Name (yourdomain.com)
```

### What is ECS?
- **ECS (Elastic Container Service)**: AWS service to run Docker containers
- **Fargate**: Serverless container running (you don't manage servers)
- **ALB**: Automatically distributes traffic to your app instances
- **RDS**: Managed PostgreSQL database
- **ElastiCache**: Managed Redis for caching

### Prerequisites

**1. AWS Account Setup**
```bash
# Install AWS CLI
aws --version  # >= 2.0

# Configure AWS credentials
aws configure
# Enter:
#   AWS Access Key ID: [YOUR_KEY]
#   AWS Secret Access Key: [YOUR_SECRET]
#   Default region: us-east-1
#   Default output format: json

# Verify configuration
aws s3 ls
```

**2. Install Required Tools**
```bash
# Terraform (Infrastructure as Code)
terraform --version  # >= 1.0

# Docker
docker --version
```

**3. Create AWS Prerequisites**
```bash
# 1. Create S3 bucket for Terraform state
aws s3 mb s3://share-task-terraform-state-$(date +%s)

# 2. Create ACM SSL Certificate (in AWS Console)
# Go to: AWS Console > Certificate Manager
# Create public certificate for yourdomain.com

# 3. Create Route53 hosted zone (if using Route53)
# Or use external DNS provider

# 4. Create EC2 Key Pair
aws ec2 create-key-pair --key-name share-task-key > share-task-key.pem
chmod 400 share-task-key.pem
```

### Step-by-Step AWS Deployment

**Step 1: Prepare Terraform Configuration**

Navigate to terraform directory:
```bash
cd terraform
```

Copy variables template:
```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit terraform.tfvars:
```bash
nano terraform.tfvars  # or use your editor
```

Example configuration:
```hcl
aws_region       = "us-east-1"
project_name     = "share-task"
environment      = "production"
app_name         = "share-task-app"
container_port   = 8000
desired_count    = 2              # Number of app instances
cpu              = "256"          # CPU units (256=0.25 vCPU)
memory           = "512"          # Memory in MB
db_username      = "postgres"
db_password      = "YourSecurePassword123!"  # Change this!
```

**Step 2: Initialize Terraform**
```bash
terraform init
# This downloads AWS plugins and prepares directory
```

**Step 3: Plan Infrastructure**
```bash
terraform plan -out=tfplan
# Shows what will be created (review carefully!)
```

**Step 4: Apply Infrastructure**
```bash
terraform apply tfplan
# Creates all AWS resources
# This takes 10-15 minutes!

# Wait for completion...
# You'll see outputs with:
#   - ALB DNS name
#   - RDS endpoint
#   - ECR repository URL
```

**Step 5: Build and Push Docker Image to AWS ECR**

```bash
# Go back to project root
cd ..

# Get ECR login credentials
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t share-task:latest .

# Tag for ECR
docker tag share-task:latest \
  YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/share-task-repo:latest

# Push to ECR
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/share-task-repo:latest
```

**Step 6: Deploy to ECS**

Option A: Via AWS Console
```
1. Go to: AWS Console > ECS Clusters
2. Select: share-task-cluster
3. Click: share-task-service
4. Click: Update service
5. Check: "Force new deployment"
6. Hit: Update Service
```

Option B: Via AWS CLI
```bash
aws ecs update-service \
  --cluster share-task-cluster \
  --service share-task-service \
  --force-new-deployment \
  --region us-east-1
```

**Step 7: Verify Deployment**

```bash
# Check service status
aws ecs describe-services \
  --cluster share-task-cluster \
  --services share-task-service \
  --region us-east-1

# View running tasks
aws ecs list-tasks \
  --cluster share-task-cluster \
  --region us-east-1

# View logs
aws logs tail /ecs/share-task-app --follow
```

**Step 8: Access Your Application**

From Terraform output, you'll see the ALB DNS name:
```
Application URL: http://share-task-alb-123456.us-east-1.elb.amazonaws.com
```

Setup custom domain (optional):
```bash
# In Route53 or your DNS provider:
# Create CNAME record pointing to ALB DNS name
yourdomain.com -> share-task-alb-123456.us-east-1.elb.amazonaws.com
```

---

## Part 4: Jenkins Setup & CI/CD Pipeline

### What is Jenkins?
Jenkins is an automation server that:
1. Watches your GitHub repository
2. When you push code, it automatically:
   - Checks out your code
   - Runs tests
   - Builds Docker image
   - Pushes to AWS ECR
   - Deploys to ECS
3. No manual deployment needed!

### Option A: Jenkins on Separate EC2 (Recommended)

**Step 1: Create EC2 Instance**
```bash
# Create EC2 instance in AWS Console
# AMI: Ubuntu 22.04 LTS
# Instance Type: t3.medium (2GB RAM minimum)
# Security Group: Allow ports 8080 (Jenkins), 22 (SSH)
# Key Pair: Use your share-task-key.pem
```

**Step 2: SSH into EC2**
```bash
ssh -i share-task-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

**Step 3: Manual Installation (Quick)**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Java (Jenkins requires Java)
sudo apt install -y openjdk-11-jdk

# Add Jenkins repository
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

# Install Jenkins
sudo apt update
sudo apt install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
# Copy this password

# Access Jenkins
# Open browser: http://YOUR_EC2_PUBLIC_IP:8080
# Paste the password you copied
```

**Step 4: Configure Jenkins Initial Setup**
1. Paste the password
2. Click "Install suggested plugins" (auto-installs necessary plugins)
3. Create first admin user
4. Configure Jenkins URL: http://YOUR_EC2_PUBLIC_IP:8080
5. Click "Start using Jenkins"

### Option B: Using Ansible (Automated)

**Step 1: Install Ansible Locally**
```bash
pip install ansible
```

**Step 2: Configure Inventory**
Edit `ansible/inventory.ini`:
```ini
[jenkins]
jenkins_host ansible_host=YOUR_EC2_PUBLIC_IP ansible_user=ubuntu ansible_ssh_private_key_file=./share-task-key.pem
```

**Step 3: Run Ansible Playbook**
```bash
cd ansible
ansible-playbook -i inventory.ini jenkins-setup.yml
```

This automates everything (same as manual steps).

### Step 5: Configure Jenkins Pipeline

**Jenkins Job Setup:**

1. **Create New Pipeline Job**
   - Jenkins Home > New Item
   - Name: "share-task-pipeline"
   - Type: Pipeline
   - Click OK

2. **Configure Pipeline Source**
   - Pipeline section > Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: https://github.com/YOUR_USERNAME/Share-Task.git
   - Credentials: Add GitHub credentials if private repo
   - Branch: main
   - Script Path: Jenkinsfile (already exists!)

3. **Add AWS Credentials to Jenkins**
   - Jenkins > Manage Jenkins > Manage Credentials
   - Click "Add Credentials"
   - Kind: "AWS Credentials"
   - Enter your AWS Access Key and Secret Key
   - ID: aws-account-id

4. **Save and Build**
   - Click Save
   - Click "Build Now"
   - Watch the pipeline execute!

### How the Pipeline Works

Jenkinsfile (automated when you push):
```
1. Checkout code from GitHub
2. Build Docker image
3. Run tests
4. Security scan (Trivy)
5. Push to AWS ECR
6. Deploy to ECS (if main branch)
7. Wait for deployment to finish
```

---

## Part 5: Complete Workflow Summary

### Local Development Workflow
```
Write Code 
  → docker-compose up -d        (Run locally)
  → Test features
  → fix bugs
  → git push origin feature-branch
  → Create Pull Request
  → Code Review
  → Merge to main
```

### Automatic Deployment (After Merge to Main)
```
Git Merge to Main
  → Jenkins triggered automatically
  → Tests run & pass
  → Docker image built
  → Image pushed to AWS ECR
  → ECS updated with new image
  → Application updates automatically
  → Users see new features!
```

---

## Part 6: Database & Environment Variables

### PostgreSQL Connection String
```
postgresql://postgres:password@db_host:5432/todolist_db
```

### Environment Variables (.env file)

**For Local Development:**
```bash
DEBUG=True
SECRET_KEY=your-random-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for dev)
USE_SQLITE=1

# Or PostgreSQL
USE_SQLITE=0
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=todolist_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

**For Production (ECS):**
```bash
DEBUG=False
SECRET_KEY=your-secure-secret-key-min-50-chars

# PostgreSQL RDS
POSTGRES_HOST=share-task-db.xxxxx.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=todolist_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password

# Redis ElastiCache
REDIS_HOST=share-task-redis.xxxxx.cache.amazonaws.com
REDIS_PORT=6379

# AWS
AWS_REGION=us-east-1
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
```

---

## Part 7: Troubleshooting

### Docker Compose Issues

**"Port 8000 already in use"**
```bash
# Option 1: Change port in docker-compose.yml
# Change ports: "1234:8000" instead of "8000:8000"

# Option 2: Kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

**"Database connection refused"**
```bash
# Wait for database to start
sleep 15

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

**"Migrations not running"**
```bash
# Manually run migrations
docker-compose exec web python todolist/manage.py migrate
```

### Jenkins Issues

**"Jenkins webpage not loading"**
```bash
# SSH to EC2
ssh -i share-task-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Check Jenkins status
sudo systemctl status jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# View logs
sudo tail -f /var/log/jenkins/jenkins.log
```

**"Build failing"**
1. Check Jenkins logs: Jenkins > Build > Console Output
2. Check Docker image building locally:
   ```bash
   docker build -t test .
   ```
3. Check ECR credentials configured correctly

### ECS Issues

**"Tasks not running"**
```bash
# Check task status
aws ecs describe-tasks \
  --cluster share-task-cluster \
  --tasks <TASK_ARN> \
  --region us-east-1

# View logs
aws logs tail /ecs/share-task-app --follow
```

**"Application not accessible"**
1. Check ALB is healthy: AWS Console > EC2 > Load Balancers
2. Check security groups allow traffic
3. Check RDS database is accessible

---

## Part 8: Important Services Ports

| Service | Port | Access |
|---------|------|--------|
| Django (Dev) | 8000 | localhost:8000 |
| Nginx | 3000 | localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Jenkins | 8080 | ec2-ip:8080 |
| Django (Production) | 8000 | internal only |

---

## Part 9: Scaling & Management

### Scale Application (ECS)
```bash
# Increase desired task count (2 → 4)
aws ecs update-service \
  --cluster share-task-cluster \
  --service share-task-service \
  --desired-count 4 \
  --region us-east-1
```

### Monitor Logs
```bash
# Real-time logs
aws logs tail /ecs/share-task-app --follow

# Specific time range
aws logs tail /ecs/share-task-app --since 1h
```

### Database Backup
```bash
# Export database
docker-compose exec db pg_dump \
  -U postgres todolist_db > backup.sql

# Restore database
docker-compose exec -T db psql \
  -U postgres todolist_db < backup.sql
```

---

## ✅ Quick Reference Checklist

### ✓ Local Development (5-10 minutes)
- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Run migrations
- [ ] Create superuser
- [ ] Run `python manage.py runserver`

### ✓ Docker Compose (10-15 minutes)
- [ ] Install Docker
- [ ] `docker-compose up -d`
- [ ] Run migrations: `docker-compose exec web python todolist/manage.py migrate`
- [ ] Create superuser
- [ ] Access http://localhost:3000

### ✓ AWS ECS Production (30-45 minutes)
- [ ] AWS account + CLI configured
- [ ] Terraform configured
- [ ] `terraform plan` + `terraform apply`
- [ ] Build Docker image
- [ ] Push to ECR
- [ ] Deploy to ECS
- [ ] Setup DNS (optional)

### ✓ Jenkins CI/CD (20-30 minutes)
- [ ] Create EC2 instance (or use Ansible)
- [ ] Install Jenkins (manually or Ansible)
- [ ] Configure Jenkins credentials
- [ ] Create Pipeline job
- [ ] Link to GitHub repository
- [ ] Pipeline automatically deploys on push!

---

## 📞 Need Help?

**Common Issues & Solutions:**
- Docker not starting? Install Docker Desktop
- Port conflicts? Use different port in docker-compose.yml
- AWS credentials? Run `aws configure` with correct keys
- Jenkins not triggering? Check GitHub webhook settings

---

**You now have everything to run Share-Task! Start with Local Development, then move to Docker Compose, then to Production ECS with Jenkins automation! 🎉**
