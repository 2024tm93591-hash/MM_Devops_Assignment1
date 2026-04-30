pipeline {
    agent any

    environment {
        PYTHON          = 'C:/python313/python.exe'
        DOCKER_HUB_USER = '2024tm93591'
        IMAGE_NAME      = 'aceest-gym'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        FULL_IMAGE      = "${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE    = "${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
        GCP_PROJECT     = 'tm93591'
        GCP_REGION      = 'us-central1'
        GKE_CLUSTER     = 'aceest-gym-cluster'
        SONAR_HOST_URL  = 'http://localhost:9000'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat "${PYTHON} -m pip install --upgrade pip"
                bat "${PYTHON} -m pip install -r requirements.txt"
                bat "${PYTHON} -m pip install pytest pytest-cov"
            }
        }

        stage('Run Tests') {
            steps {
                bat "${PYTHON} -m pytest tests/ -v --tb=short --cov=. --cov-report=xml:coverage.xml --cov-report=term-missing"
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: '**/test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    bat """
                        C:\\sonar-scanner\\bin\\sonar-scanner.bat ^
                          -Dsonar.projectKey=aceest-gym ^
                          -Dsonar.projectName=ACEest-Fitness-Gym ^
                          -Dsonar.projectVersion=${IMAGE_TAG} ^
                          -Dsonar.sources=. ^
                          -Dsonar.exclusions=**/tests/**,**/__pycache__/**,**/instance/** ^
                          -Dsonar.python.coverage.reportPaths=coverage.xml ^
                          -Dsonar.host.url=${SONAR_HOST_URL} ^
                          -Dsonar.token=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t ${FULL_IMAGE} -t ${LATEST_IMAGE} ."
                bat "docker images | findstr ${IMAGE_NAME}"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin"
                    bat "docker push ${FULL_IMAGE}"
                    bat "docker push ${LATEST_IMAGE}"
                    bat "docker logout"
                }
            }
        }

        stage('Configure kubectl') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY_FILE')]) {
                    bat "gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}"
                    bat "gcloud config set project ${GCP_PROJECT}"
                    bat "gcloud container clusters get-credentials ${GKE_CLUSTER} --region ${GCP_REGION} --project ${GCP_PROJECT}"
                }
            }
        }

        stage('Deploy: Rolling Update') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    bat "powershell -Command \"(Get-Content k8s/rolling-update.yaml) -replace 'IMAGE_PLACEHOLDER', '${FULL_IMAGE}' | Set-Content k8s/rolling-update.yaml\""
                    bat "kubectl apply -f k8s/rolling-update.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-rolling --timeout=300s"
                }
            }
        }

        stage('Deploy: Blue-Green') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    bat "powershell -Command \"(Get-Content k8s/blue-green.yaml) -replace 'IMAGE_PLACEHOLDER', '${FULL_IMAGE}' | Set-Content k8s/blue-green.yaml\""
                    bat "kubectl apply -f k8s/blue-green.yaml"
                    bat "kubectl set selector svc/aceest-gym-bg-svc version=green"
                    bat "kubectl rollout status deployment/aceest-gym-green --timeout=600s"
                }
            }
        }

    }

    post {
        success {
            echo "SUCCESS - image ${FULL_IMAGE} deployed to GKE (Rolling Update -> Blue-Green)."
        }
        failure {
            echo "FAILED - initiating rollback on rolling-update deployment."
            bat "kubectl rollout undo deployment/aceest-gym-rolling || true"
        }
        always {
            bat "docker rmi ${FULL_IMAGE} ${LATEST_IMAGE} || true"
            cleanWs()
        }
    }
}pipeline {
    agent any

    environment {
        PYTHON          = 'python3'
        DOCKER_HUB_USER = '2024tm93591'
        IMAGE_NAME      = 'aceest-gym'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        FULL_IMAGE      = "${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE    = "${DOCKER_HUB_USER}/${IMAGE_NAME}:latest"
        GCP_PROJECT     = 'tm93591'
        GCP_REGION      = 'us-central1'
        GKE_CLUSTER     = 'aceest-gym-cluster'
        SONAR_HOST_URL  = 'http://localhost:9000'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '$PYTHON -m pip install --upgrade pip'
                sh '$PYTHON -m pip install -r requirements.txt'
                sh '$PYTHON -m pip install pytest pytest-cov'
            }
        }

        stage('Run Tests') {
            steps {
                sh '$PYTHON -m pytest tests/ -v --tb=short --cov=. --cov-report=xml:coverage.xml --cov-report=term-missing'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: '**/test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=aceest-gym \
                          -Dsonar.projectName='ACEest Fitness & Gym' \
                          -Dsonar.projectVersion=${IMAGE_TAG} \
                          -Dsonar.sources=. \
                          -Dsonar.exclusions='**/tests/**,**/__pycache__/**,**/instance/**' \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.host.url=${SONAR_HOST_URL} \
                          -Dsonar.token=${SONAR_TOKEN}
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${FULL_IMAGE} -t ${LATEST_IMAGE} ."
                sh "docker images | grep ${IMAGE_NAME}"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                    sh "docker push ${FULL_IMAGE}"
                    sh "docker push ${LATEST_IMAGE}"
                    sh "docker logout"
                }
            }
        }

        stage('Configure kubectl') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY_FILE')]) {
                    sh "gcloud auth activate-service-account --key-file=$GCP_KEY_FILE"
                    sh "gcloud config set project ${GCP_PROJECT}"
                    sh "gcloud container clusters get-credentials ${GKE_CLUSTER} --region ${GCP_REGION} --project ${GCP_PROJECT}"
                }
            }
        }

        stage('Deploy: Rolling Update') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh "sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' k8s/rolling-update.yaml"
                    sh "kubectl apply -f k8s/rolling-update.yaml"
                    sh "kubectl rollout status deployment/aceest-gym-rolling --timeout=300s"
                }
            }
        }

        stage('Deploy: Blue-Green') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh "sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' k8s/blue-green.yaml"
                    sh "kubectl apply -f k8s/blue-green.yaml"
                    sh "kubectl set selector svc/aceest-gym-bg-svc version=green"
                    sh "kubectl rollout status deployment/aceest-gym-green --timeout=300s"
                }
            }
        }

    }

    post {
        success {
            echo "SUCCESS - image ${FULL_IMAGE} deployed to GKE (Rolling Update -> Blue-Green)."
        }
        failure {
            echo "FAILED - initiating rollback on rolling-update deployment."
            sh "kubectl rollout undo deployment/aceest-gym-rolling || true"
        }
        always {
            sh "docker rmi ${FULL_IMAGE} ${LATEST_IMAGE} || true"
            cleanWs()
        }
    }
}
