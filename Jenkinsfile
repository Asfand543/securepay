pipeline {
    agent any

    environment {
        APP_NAME = "securepay"
        IMAGE_NAME = "securepay:latest"
        NAMESPACE = "securepay"
        K8S_DIR = "k8s"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Verify Files') {
            steps {
                sh '''
                pwd
                ls -la
                ls -la ${K8S_DIR}
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t ${IMAGE_NAME} -f dockerfile .
                '''
            }
        }

        stage('Load Image into Minikube') {
            steps {
                sh '''
                minikube image load ${IMAGE_NAME}
                '''
            }
        }

        stage('Deploy Namespace') {
            steps {
                sh '''
                kubectl apply -f ${K8S_DIR}/namespace.yaml
                '''
            }
        }

        stage('Deploy PVC') {
            steps {
                sh '''
                kubectl apply -f ${K8S_DIR}/pvc.yaml
                '''
            }
        }

        stage('Deploy App to Kubernetes') {
            steps {
                sh '''
                kubectl apply -f ${K8S_DIR}/deployment.yaml
                kubectl apply -f ${K8S_DIR}/service.yaml
                '''
            }
        }

        stage('Restart Deployment') {
            steps {
                sh '''
                kubectl rollout restart deployment/${APP_NAME}-app -n ${NAMESPACE}
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                kubectl get all -n ${NAMESPACE}
                kubectl get pvc -n ${NAMESPACE}
                '''
            }
        }
    }

    post {
        success {
            echo 'SecurePay application deployed successfully to Kubernetes!'
        }
        failure {
            echo 'Pipeline failed. Check logs for troubleshooting.'
        }
    }
}
