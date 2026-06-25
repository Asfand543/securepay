```groovy
pipeline {
    agent any

    environment {
        APP_NAME   = "securepay"
        IMAGE_NAME = "securepay:latest"
        NAMESPACE  = "securepay"
        K8S_DIR    = "k8s"
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
                    set -e
                    pwd
                    ls -la
                    ls -la ${K8S_DIR}
                '''
            }
        }

        stage('Verify Tools') {
            steps {
                sh '''
                    set -e
                    docker --version
                    kubectl version --client
                    kubectl get ns
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
                    docker build -t ${IMAGE_NAME} -f dockerfile .
                    docker images | grep securepay
                '''
            }
        }

        stage('Load Image into Minikube') {
            steps {
                sh '''
                    set -e
                    docker save ${IMAGE_NAME} -o /tmp/securepay.tar
                    docker cp /tmp/securepay.tar minikube:/tmp/securepay.tar
                    docker exec minikube sh -c "ls -lh /tmp/securepay.tar && docker load -i /tmp/securepay.tar"
                '''
            }
        }

        stage('Deploy Namespace') {
            steps {
                sh '''
                    set -e
                    kubectl apply -f ${K8S_DIR}/namespace.yaml
                '''
            }
        }

        stage('Deploy PVC') {
            steps {
                sh '''
                    set -e
                    kubectl apply -f ${K8S_DIR}/pvc.yaml
                '''
            }
        }

        stage('Deploy App to Kubernetes') {
            steps {
                sh '''
                    set -e
                    kubectl apply -f ${K8S_DIR}/deployment.yaml
                    kubectl apply -f ${K8S_DIR}/service.yaml
                '''
            }
        }

        stage('Restart Deployment') {
            steps {
                sh '''
                    set -e
                    kubectl rollout restart deployment/${APP_NAME}-app -n ${NAMESPACE}
                    kubectl rollout status deployment/${APP_NAME}-app -n ${NAMESPACE} --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    set -e
                    echo "=== Pods ==="
                    kubectl get pods -n ${NAMESPACE} -o wide

                    echo "=== Services ==="
                    kubectl get svc -n ${NAMESPACE}

                    echo "=== PVC ==="
                    kubectl get pvc -n ${NAMESPACE}

                    echo "=== Endpoints ==="
                    kubectl get endpoints -n ${NAMESPACE}
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
        always {
            script {
                try {
                    sh 'rm -f /tmp/securepay.tar || true'
                } catch (Exception e) {
                    echo 'Skipping cleanup because workspace/context was not available.'
                }
            }
        }
    }
}
```

