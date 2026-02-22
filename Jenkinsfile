pipeline {
    agent any

    environment {
        IMAGE = "share-task-app:${BUILD_NUMBER}"
        KUBECONFIG = "${HOME}/.kube/config"
    }

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
    }

    stages {

        stage('1. Checkout Code') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('2. Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh """
                    docker build -t ${IMAGE} .
                """
            }
        }

        stage('3. Run Tests') {
            steps {
                echo "Running application tests..."
                sh """
                    docker run --rm ${IMAGE} python manage.py test --noinput
                """
            }
        }

        stage('4. Deploy to Kubernetes') {
            steps {
                echo "Deploying to local Kubernetes..."
                sh """
                    kubectl set image deployment/todolist-app \
                    todolist=${IMAGE} -n default || true

                    kubectl rollout status deployment/todolist-app \
                    -n default --timeout=120s || true
                """
            }
        }

        stage('5. Health Check') {
            steps {
                echo "Checking pod and service status..."
                sh """
                    kubectl get pods -n default
                    kubectl get svc -n default
                """
            }
        }
    }

    post {
        always {
            echo "Cleaning unused Docker images..."
            sh "docker image prune -f"
        }

        success {
            echo "Pipeline completed successfully!"
        }

        failure {
            echo "Pipeline failed!"
        }
    }
}