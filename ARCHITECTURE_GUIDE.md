# Share-Task Architecture & Deployment Paths

## 🎯 Three Ways to Deploy - Choose Your Level

### Level 1: Local Python Environment
**Complexity:** ⭐☆☆ | **Time:** 5 min | **Cost:** Free

```
Your Computer
    ↓
Virtual Environment (venv)
    ↓
Python Dependencies Installed
    ↓
Django Dev Server (localhost:8000)
    ↓
SQLite Database (local file)
    ↓
✅ Running Locally
```

**Good for:**
- Learning Django
- Development & testing
- No external services needed

---

### Level 2: Docker Compose (Local Full Stack)
**Complexity:** ⭐⭐☆ | **Time:** 10 min | **Cost:** Free

```
Your Computer
    ↓
Docker Daemon
    ├─→ PostgreSQL Container (Database)
    ├─→ Redis Container (Cache)
    ├─→ Django Container (App)
    ├─→ Celery Container (Background jobs)
    ├─→ Celery Beat Container (Scheduler)
    └─→ Nginx Container (Reverse proxy)
    ↓
http://localhost:3000 (Nginx)
    ↓
✅ Full Stack Running
```

**Good for:**
- Testing with real database
- Testing background tasks
- Testing production setup locally
- Demo to stakeholders

---

### Level 3: AWS ECS (Production Cloud)
**Complexity:** ⭐⭐⭐ | **Time:** 45-60 min | **Cost:** $50-200/month

```
┌─────────────────────────────────────────────────────────┐
│                    INTERNET / DNS                        │
│              yourdomain.com (Route53)                    │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │   AWS ALB      │
         │ (Load Balancer)│
         │   Port 80, 443 │
         └────────┬───────┘
                  │
         ┌────────▼─────────┐
         │   ECS Cluster    │
         │  (AWS Fargate)   │
         │                  │
         ├─ Task 1 (Django) │
         ├─ Task 2 (Django) │
         ├─ Task 3 (Django) │
         └─ Auto-scaler    │ ← Scales 2-4 based on load
                  │
         ┌────────┼────────┐
         │        │        │
    ┌────▼───┐┌───▼────┐┌─▼──────────┐
    │AWS RDS ││ElastiC ││CloudWatch │
    │(DB)    ││ache    ││(Logs)     │
    │Postgres││(Redis) ││           │
    └────────┘└────────┘└───────────┘
         │
    ✅ Production Ready
    Auto-scaling, monitoring, backups
```

---

## 🔄 CI/CD Pipeline Architecture

### With Jenkins on EC2

```
┌──────────────────┐
│  Your Laptop     │
│                  │
│  git push        │
│  to GitHub       │
│  (main branch)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  GitHub Repository   │
│                      │
│  Webhook triggers    │
│  Jenkins             │
└────────┬─────────────┘
         │
         ▼
    ┌────────────────────────────────────┐
    │   Jenkins on EC2 (t3.medium)       │
    │   (CI/CD Orchestrator)             │
    │                                    │
    │  Stage 1: Checkout Code            │
    │    ↓                               │
    │  Stage 2: Run Tests                │
    │    ↓                               │
    │  Stage 3: Build Docker Image       │
    │    ↓                               │
    │  Stage 4: Security Scan (Trivy)    │
    │    ↓                               │
    │  Stage 5: Push to AWS ECR          │
    │    ↓                               │
    │  Stage 6: Deploy to ECS            │
    │    ↓                               │
    │  Stage 7: Health Check             │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────┐
    │   AWS ECR         │
    │ (Image Registry)  │
    │                   │
    │ share-task:build  │
    │ -number-1234      │
    └────────┬──────────┘
             │
    ┌────────▼───────────────┐
    │   AWS ECS Service       │ ← Auto pulls new image
    │                         │
    │ → Updates running tasks │
    │ → Zero downtime deploy  │
    │ → Auto scaling works    │
    └─────────────────────────┘
         │
         ▼
    ✅ New version live!
    Users see changes automatically
```

---

## 📊 Database Architecture

### PostgreSQL Setup in ECS

```
┌─────────────────────────────────────┐
│  ECS Tasks (Application Layer)      │
│  ├─ Django Container 1              │
│  ├─ Django Container 2              │
│  ├─ Django Container 3              │
│  └─ Celery Container                │
└─────────────────┬───────────────────┘
                  │
        ┌─────────▼──────────┐
        │   AWS RDS         │
        │   PostgreSQL 15   │
        │                   │
        │ ├─ Primary DB    │ ← Writes here
        │ └─ Standby DB    │ ← Auto failover
        │                   │
        │ Multi-AZ Enabled │ ← Always available
        │ Backups: Daily   │
        │ Retention: 30 days│
        └───────────────────┘
```

---

## 💾 Cache & Queue Architecture

### Redis for Caching & Task Queue

```
┌─────────────────────────────────────┐
│     ECS Django Tasks                │
└──────────────┬──────────────────────┘
               │
      ┌────────▼────────┐
      │  AWS ElastiC    │
      │  Cache (Redis)  │
      │                 │
      │ Session Cache   │
      │ Task Queue      │
      │ Real-time Data  │
      │                 │
      │ Replication: 2  │ ← High availability
      │ Auto-failover   │
      └─────────────────┘
```

---

## 🔐 Security Architecture

```
┌──────────────┐
│   Internet   │
│  (Attackers) │
└────────┬─────┘
         │
   ┌─────▼────────┐
   │ AWS Shield   │ ← DDoS protection
   └─────┬────────┘
         │
   ┌─────▼────────────────┐
   │  AWS WAF             │ ← Web firewall
   └─────┬────────────────┘
         │
   ┌─────▼────────────┐
   │  Security Group  │ ← Source IP filtering
   │  (VPC Firewall)  │
   └─────┬────────────┘
         │
   ┌─────▼──────────────┐
   │  Load Balancer     │
   │  (HTTPS/SSL)       │
   └─────┬──────────────┘
         │
   ┌─────▼────────────┐
   │  Private Subnet  │ ← Only accessible via ALB
   │                  │
   │  ├─ ECS Cluster  │
   │  └─ RDS Database │
   │     (Not public) │
   └──────────────────┘

Secrets stored in AWS Secrets Manager
Encrypted in transit (HTTPS/TLS)
Encrypted at rest (encrypted volumes)
```

---

## 📈 Scaling Strategy

### Auto-Scaling Groups

```
Load increases
    ↓
┌─────────────────────────────────┐
│  Application Load Balancer      │
│  Monitors CPU & Memory          │
└──────────────┬──────────────────┘
               │
        ┌──────▼──────┐
        │  CPU > 70%? │
        └──────┬──────┘
               │
        ┌──────▼────────┐
        │ Yes → Scale   │
        │ Up Containers │
        └───────────────┘
               ↓
    ┌──────────────────────┐
    │  ECS Auto Scaling    │
    │                      │
    │ Min Desired:  2      │
    │ Max Desired:  4      │
    │ Target CPU:  70%     │
    └──────────────────────┘
               ↓
    ┌──────────────────────┐
    │ New Docker Container │
    │ Started in seconds   │
    │ Registered to ALB    │
    └──────────────────────┘
```

---

## 🔄 Update & Deployment Flow

### Zero-Downtime Deployment

```
v1.0.0 Running
├─ Container A
├─ Container B
└─ Container C
    ↓
Jenkins pushes v2.0.0 image to ECR
    ↓
ECS Rolling Update Begins
    │
    ├─ Start Container D (v2.0.0)
    │  └─ Add to ALB when healthy
    │
    ├─ Stop Container A (v1.0.0)
    │  └─ Drain traffic first
    │
    ├─ Start Container E (v2.0.0)
    │  └─ Add to ALB when healthy
    │
    ├─ Stop Container B (v1.0.0)
    │  └─ Drain traffic first
    │
    ├─ Start Container F (v2.0.0)
    │  └─ Add to ALB when healthy
    │
    └─ Stop Container C (v1.0.0)
       └─ Drain traffic first
    ↓
v2.0.0 Now Running
├─ Container D
├─ Container E
└─ Container F
    ↓
✅ Zero Downtime! Users never see outage
```

---

## 🏭 Application Components

```
┌──────────────────────────────────────────────────────┐
│                   Users/Browsers                      │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Nginx (Static Proxy) │
        │   ├─ CSS/JS (CDN ready)│
        │   └─ Media files       │
        └───────────┬────────────┘
                    │
                    ▼
        ┌──────────────────────────────┐
        │  Django Application (Backend) │
        │                              │
        │  ├─ ai_task_management/      │
        │  ├─ chat/                    │
        │  ├─ user/                    │
        │  ├─ task/                    │
        │  ├─ leaderboard/             │
        │  ├─ notes_app/               │
        │  ├─ subscription/            │
        │  └─ templatetags/            │
        └───────────┬──────────────────┘
                    │
        ┌───────────┼──────────┐
        │           │          │
        ▼           ▼          ▼
    ┌────────┐ ┌────────┐ ┌─────────┐
    │Database│ │ Cache  │ │ Queue   │
    │ RDS    │ │ Redis  │ │ Celery  │
    │        │ │        │ │ Worker  │
    └────────┘ └────────┘ └─────────┘
        │           │          │
        └───────────┼──────────┘
                    │
        ┌───────────▼──────────┐
        │ Background Tasks     │
        │ ├─ Email sent        │
        │ ├─ Notifications     │
        │ ├─ Scheduled tasks   │
        │ └─ Report generation │
        └──────────────────────┘
```

---

## 🔌 Ansible vs Manual Jenkins Installation

### Ansible (Automated - 5 minutes)

```
Your Laptop
    ↓
ansible-playbook jenkins-setup.yml
    ↓
Ansible connects to EC2 via SSH
    ├─ Runs: sudo apt update
    ├─ Installs: Java 11
    ├─ Adds: Jenkins repository
    ├─ Installs: Jenkins package
    ├─ Starts: Jenkins service
    ├─ Installs: Plugins automatically
    └─ Returns: Admin password
    ↓
Jenkins ready to use!
```

### Manual (20 minutes)

```
Your Laptop
    ↓
SSH into EC2
    ↓
Run commands one by one:
    ├─ sudo apt update
    ├─ sudo apt install java-11-openjdk-devel
    ├─ Add repository manually
    ├─ sudo apt install jenkins
    ├─ sudo systemctl start jenkins
    ├─ Get password from /var/lib/jenkins/secrets/
    ├─ Access web UI
    ├─ Install plugins manually
    └─ Configure settings
    ↓
Jenkins setup complete
```

**Ansible is 4x faster and can re-run on multiple servers!**

---

## 📋 Decision Tree: Which Setup Should I Use?

```
START HERE
    │
    ├─ "I just want to try it locally"
    │   └─ Use Local Python Setup (5 min)
    │       → python manage.py runserver
    │
    ├─ "I want to test real features (DB, cache, etc)"
    │   └─ Use Docker Compose (10 min)
    │       → docker-compose up -d
    │
    ├─ "I want production in cloud"
    │   └─ Use AWS ECS (45 min)
    │
    │       "How do I automate deployments?"
    │       │
    │       ├─ "I'm learning DevOps"
    │       │   └─ Setup Jenkins manually
    │       │       → SSH to EC2, install step by step
    │       │
    │       └─ "I want fast automation"
    │           └─ Use Ansible
    │               → ansible-playbook jenkins-setup.yml
    │
    └─ "I want everything automated on day 1"
        └─ Use Terraform + Ansible combo (90 min total)
            → terraform apply (creates AWS)
            → ansible-playbook (installs Jenkins)
            → Result: Fully automated CI/CD pipeline
```

---

## 📊 Cost Breakdown (AWS/Month)

```
┌─────────────────────────────────────────┐
│        AWS ECS Production Setup          │
├─────────────────────────────────────────┤
│                                         │
│ ECS Fargate (2 tasks @ $0.01/hr)       │ $15
│   └─ 0.25 vCPU, 512 MB RAM per task   │
│                                         │
│ RDS PostgreSQL (db.t3.micro)           │ $15
│   └─ Multi-AZ enabled                  │
│                                         │
│ ElastiCache Redis (cache.t3.micro)    │ $12
│   └─ Replication enabled               │
│                                         │
│ NAT Gateway (data transfer)             │ $16
│                                         │
│ ALB (Application Load Balancer)         │ $15
│                                         │
│ CloudWatch Logs & Monitoring            │ $5
│                                         │
│ Domain Name (Route53 or external)       │ $0-12
│                                         │
├─────────────────────────────────────────┤
│ TOTAL MONTHLY COST: $78 - $90           │
├─────────────────────────────────────────┤
│ Scale up example:                       │
│ 4 tasks + db.t3.small + cache.t3.small │ $150-200
└─────────────────────────────────────────┘

* Free tier: First 12 months AWS includes some free usage
* Local development: FREE
* Docker Compose: FREE
```

---

## ✅ Next Steps

1. **START NOW**: Choose one setup above
2. **ASK QUESTIONS**: Check COMPLETE_RUN_GUIDE.md
3. **USE COMMANDS**: Reference QUICK_COMMANDS.md
4. **MONITOR LOGS**: Use docker-compose logs or AWS CloudWatch
5. **ITERATE**: Develop locally, test with Docker Compose, deploy to AWS

**Happy deploying! 🚀**
