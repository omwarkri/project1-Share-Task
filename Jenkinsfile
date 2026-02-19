pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPOSITORY = 'share-task-repo'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_IMAGE = "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
        ECS_CLUSTER = 'share-task-cluster'
        ECS_SERVICE = 'share-task-service'
        KUBE_CONFIG = credentials('kubeconfig')
    }

    options {
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out code from repository..."
                    checkout scm
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "🏗️  Building Docker image..."
                    sh '''
                        docker build -t ${DOCKER_IMAGE} .
                        docker tag ${DOCKER_IMAGE} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    echo "🧪 Running tests..."
                    sh '''
                        docker run --rm ${DOCKER_IMAGE} \
                            python todolist/manage.py test --keepdb --noinput
                    '''
                }
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    echo "🔒 Scanning image for vulnerabilities..."
                    sh '''
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                            aquasec/trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}
                    '''
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    echo "📤 Pushing image to ECR..."
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker push ${DOCKER_IMAGE}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                    '''
                }
            }
        }

        stage('Deploy to ECS') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🚀 Deploying to ECS..."
                    sh '''
                        aws ecs update-service \
                            --cluster ${ECS_CLUSTER} \
                            --service ${ECS_SERVICE} \
                            --force-new-deployment \
                            --region ${AWS_REGION}
                        
                        # Wait for deployment to complete
                        aws ecs wait services-stable \
                            --cluster ${ECS_CLUSTER} \
                            --services ${ECS_SERVICE} \
                            --region ${AWS_REGION}
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "☸️  Deploying to Kubernetes..."
                    sh '''
                        export KUBECONFIG=${KUBE_CONFIG}
                        kubectl set image deployment/todolist-app \
                            todolist=${DOCKER_IMAGE} \
                            -n todolist
                        
                        # Wait for rollout to complete
                        kubectl rollout status deployment/todolist-app \
                            -n todolist --timeout=5m
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo "💓 Performing health checks..."
                    sh '''
                        # Wait for service to be healthy
                        sleep 10
                        
                        # Check ECS service health
                        aws ecs describe-services \
                            --cluster ${ECS_CLUSTER} \
                            --services ${ECS_SERVICE} \
                            --region ${AWS_REGION} | jq '.services[0].deployments'
                    '''
                }
            }
        }

        stage('Notify') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "📢 Deployment successful!"
                    sh '''
                        echo "✅ Deployment completed successfully"
                        echo "Docker Image: ${DOCKER_IMAGE}"
                        echo "ECR Repository: ${ECR_REGISTRY}/${ECR_REPOSITORY}"
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "🧹 Cleaning up..."
                sh 'docker system prune -f'
            }
        }
        failure {
            script {
                echo "❌ Pipeline failed!"
                // Add notification logic here (Slack, Email, etc.)
            }
        }
        success {
            script {
                echo "✅ Pipeline completed successfully!"
                // Add notification logic here
            }
        }
    }
}
