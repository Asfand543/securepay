pipeline {
    agent any

    environment {
        IMAGE_NAME = "securepay"
        CONTAINER_NAME = "securepay_container"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t securepay .'
            }
        }

        stage('Stop Old Container') {
            steps {
                sh '''
                docker stop securepay_container || true
                docker rm securepay_container || true
                '''
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                docker run -d \
                --name securepay_container \
                -p 8000:8000 \
                securepay
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                sleep 10
                curl -f http://localhost:8000 || exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "✅ securepay deployed successfully"
        }
        failure {
            echo "❌ Deployment failed"
        }
    }
}
