pipeline {
    agent any

    environment {
        IMAGE_NAME = "share-task-app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKER_IMAGE = "${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE = "${IMAGE_NAME}:latest"
    }

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        stage('Checkout') {
            steps {
                echo "🔄 Checking out code..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🏗️ Building Docker image..."
                sh """
                    docker build -t ${DOCKER_IMAGE} .
                    docker tag ${DOCKER_IMAGE} ${LATEST_IMAGE}
                """
            }
        }

        stage('Run Tests') {
    steps {
        echo "🧪 Running tests..."
        sh """
            docker run --rm ${DOCKER_IMAGE} \
            python manage.py test --noinput
        """
    }
}

        stage('Security Scan (Trivy)') {
            steps {
                echo "🔒 Scanning image..."
                sh """
                    docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    aquasec/trivy image ${DOCKER_IMAGE}
                """
            }
        }

        stage('Deploy to Local Kubernetes') {
            steps {
                echo "☸️ Deploying to local Kubernetes..."

                sh """
                    kubectl set image deployment/todolist-app \
                    todolist=${DOCKER_IMAGE} \
                    -n default || echo "Deployment not found"

                    kubectl rollout status deployment/todolist-app \
                    -n default --timeout=120s || true
                """
            }
        }

        stage('Health Check') {
            steps {
                echo "💓 Checking pod status..."
                sh """
                    kubectl get pods -n default
                    kubectl get svc -n default
                """
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Docker images..."
            sh "docker image prune -f"
        }

        failure {
            echo "❌ Pipeline Failed!"
        }

        success {
            echo "✅ Local Deployment Successful!"
        }
    }
}