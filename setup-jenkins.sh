#!/bin/bash

# 🚀 Jenkins + Ansible Auto-Setup Script
# This script will:
# 1. Create EC2 instance for Jenkins
# 2. Setup Ansible
# 3. Install Jenkins automatically

set -e

echo "═══════════════════════════════════════════════════════════════════════"
echo "  🔄 Jenkins Auto-Setup with Ansible"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

aws --version > /dev/null 2>&1 || { echo "❌ AWS CLI not found"; exit 1; }
echo "✅ AWS CLI found"

terraform --version > /dev/null 2>&1 || { echo "❌ Terraform not found"; exit 1; }
echo "✅ Terraform found"

# Create EC2 security group and instance
echo ""
echo "🏗️  Creating EC2 instance for Jenkins..."
echo ""

# Get user's IP
read -p "Enter your public IP (for SSH access, find at whatismyipaddress.com): " USER_IP

# Create Jenkins EC2 instance
cat > terraform/jenkins-ec2.tf << EOF
resource "aws_security_group" "jenkins" {
  name = "jenkins-sg"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["\${var.user_ip}/32"]
  }
  
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jenkins-sg"
  }
}

resource "aws_instance" "jenkins" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  
  vpc_security_group_ids = [aws_security_group.jenkins.id]
  
  key_name = "share-task-key"
  
  tags = {
    Name = "jenkins-server"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

output "jenkins_public_ip" {
  value       = aws_instance.jenkins.public_ip
  description = "Public IP of Jenkins server"
}

variable "user_ip" {
  description = "Your public IP for SSH access"
  type        = string
  default     = "\${USER_IP}"
}
EOF

echo ""
echo "Creating Terraform resources..."
cd terraform
terraform init
terraform apply -auto-approve -var="user_ip=${USER_IP}"

JENKINS_IP=$(terraform output -raw jenkins_public_ip)
cd ..

echo "✅ EC2 Instance created!"
echo "   Jenkins IP: $JENKINS_IP"
echo ""

# Wait for instance to boot
echo "⏳ Waiting for instance to boot (30 seconds)..."
sleep 30

# Setup Ansible
echo ""
echo "📝 Setting up Ansible..."
echo ""

cat > ansible/inventory.ini << EOF
[jenkins]
jenkins_server ansible_host=${JENKINS_IP} ansible_user=ubuntu \
  ansible_ssh_private_key_file=~/share-task-key.pem
EOF

echo "✅ Ansible inventory configured"
echo ""

# Install Ansible if not present
if ! command -v ansible &> /dev/null; then
    echo "📥 Installing Ansible..."
    pip install ansible
    echo "✅ Ansible installed"
else
    echo "✅ Ansible already installed"
fi

echo ""
echo "🚀 Running Ansible to install Jenkins..."
echo ""

cd ansible

# Run playbook
ansible-playbook -i inventory.ini jenkins-setup.yml

echo ""
echo "✅ Jenkins installation complete!"
echo ""

cd ..

# Display summary
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "✅ JENKINS IS READY!"
echo ""
echo "📱 Access Jenkins at:"
echo "   http://${JENKINS_IP}:8080"
echo ""
echo "📝 Next steps:"
echo "   1. Open browser to http://${JENKINS_IP}:8080"
echo "   2. Get admin password from Jenkins output above"
echo "   3. Complete initial setup"
echo "   4. Add AWS credentials"
echo "   5. Create pipeline job"
echo ""
echo "📚 See JENKINS_SETUP.md for detailed configuration"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
