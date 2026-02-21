#!/bin/bash
# Deploy Jenkins using Terraform
# Usage: ./deploy-jenkins.sh [enable|disable]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/terraform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Jenkins Terraform Deployment Script       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

# Check if terraform is initialized
if [ ! -d "$TERRAFORM_DIR/.terraform" ]; then
    echo -e "${YELLOW}Terraform not initialized. Initializing...${NC}"
    cd "$TERRAFORM_DIR"
    terraform init
fi

cd "$TERRAFORM_DIR"

# Parse argument
ACTION="${1:-enable}"

if [ "$ACTION" = "enable" ]; then
    echo -e "${YELLOW}Deploying Jenkins...${NC}"
    
    # Show plan first
    echo -e "${BLUE}Generating Terraform plan...${NC}"
    terraform plan -var="enable_jenkins=true" -out=/tmp/jenkins-plan.tfplan
    
    echo -e "${YELLOW}Review the plan above. Proceed with deployment? (yes/no)${NC}"
    read -r CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
    fi
    
    # Apply terraform
    echo -e "${BLUE}Applying Terraform configuration...${NC}"
    terraform apply /tmp/jenkins-plan.tfplan
    
    echo -e "${GREEN}Jenkins deployment started!${NC}"
    echo ""
    echo -e "${BLUE}Getting Jenkins details...${NC}"
    
    # Get outputs
    JENKINS_IP=$(terraform output -raw jenkins_public_ip)
    JENKINS_URL=$(terraform output -raw jenkins_url)
    
    echo ""
    echo -e "${GREEN}✓ Jenkins deployed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Jenkins URL:${NC} $JENKINS_URL"
    echo -e "${BLUE}Jenkins IP:${NC} $JENKINS_IP"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Wait 3-5 minutes for Jenkins to fully start"
    echo "2. Get initial password:"
    echo "   ssh -i ~/.aws/share-task-key.pem ubuntu@$JENKINS_IP"
    echo "   sudo cat /var/lib/jenkins/secrets/initialAdminPassword"
    echo "3. Open Jenkins URL in browser and complete setup"
    echo "4. Add GitHub and AWS credentials"
    echo "5. Create pipeline job from Jenkinsfile"
    echo ""
    echo -e "${BLUE}For detailed instructions, see: JENKINS_TERRAFORM_GUIDE.md${NC}"
    
elif [ "$ACTION" = "disable" ]; then
    echo -e "${YELLOW}Removing Jenkins infrastructure...${NC}"
    
    echo -e "${YELLOW}This will DESTROY Jenkins EC2 instance. Continue? (yes/no)${NC}"
    read -r CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${RED}No changes made${NC}"
        exit 1
    fi
    
    # Disable Jenkins and apply
    terraform apply -var="enable_jenkins=false" -auto-approve
    
    echo -e "${GREEN}Jenkins infrastructure removed${NC}"
    
elif [ "$ACTION" = "status" ]; then
    echo -e "${BLUE}Jenkins Status:${NC}"
    terraform output | grep jenkins || echo -e "${YELLOW}Jenkins not deployed${NC}"
    
elif [ "$ACTION" = "destroy" ]; then
    echo -e "${RED}WARNING: This will destroy ALL infrastructure including ECS and Jenkins${NC}"
    echo -e "${YELLOW}Continue? (yes/no)${NC}"
    read -r CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${RED}Cancelled${NC}"
        exit 1
    fi
    
    terraform destroy
    
else
    echo -e "${YELLOW}Usage: $0 [enable|disable|status|destroy]${NC}"
    echo ""
    echo "  enable   - Deploy Jenkins on AWS EC2"
    echo "  disable  - Remove Jenkins infrastructure"
    echo "  status   - Show Jenkins status and URLs"
    echo "  destroy  - Destroy all infrastructure"
    exit 1
fi
