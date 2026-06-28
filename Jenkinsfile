pipeline {
    agent any

    environment {
        APP_NAME   = "securepay"
        IMAGE_NAME = "asfand348/securepay"
        IMAGE_TAG  = "v1"
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
                pwd
                ls -la
                ls -la ${K8S_DIR}
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f dockerfile .
                docker images | grep securepay
                '''
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {

                    sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                docker push ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                kubectl apply -f ${K8S_DIR}/namespace.yaml
                kubectl apply -f ${K8S_DIR}/pvc.yaml
                kubectl apply -f ${K8S_DIR}/deployment.yaml
                kubectl apply -f ${K8S_DIR}/service.yaml
                '''
            }
        }

        stage('Restart Deployment') {
            steps {
                sh '''
                kubectl rollout restart deployment/${APP_NAME}-app -n ${NAMESPACE}
                kubectl rollout status deployment/${APP_NAME}-app -n ${NAMESPACE}
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                kubectl get pods -n ${NAMESPACE}
                kubectl get svc -n ${NAMESPACE}
                '''
            }
        }
    }

    post {
        success {
            echo "Deployment Successful"
        }

        failure {
            echo "Deployment Failed"
        }
    }
}
