pipeline {
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
        // Jenkins credentials IDs (configure in Jenkins -> Manage Credentials)
        // DOCKER_CREDS   : Username/Password for Docker Hub  (id: docker-hub-creds)
        // SONAR_TOKEN    : Secret text for SonarQube token   (id: sonar-token)
        // GCP_SA_KEY     : Secret file for GCP service account key (id: gcp-sa-key)
    }

    stages {

        // ---------------------------------------------
        // 1. CHECKOUT
        // ---------------------------------------------
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ---------------------------------------------
        // 2. INSTALL DEPENDENCIES
        // ---------------------------------------------
        stage('Install Dependencies') {
            steps {
                sh '$PYTHON -m pip install --upgrade pip'
                sh '$PYTHON -m pip install -r requirements.txt'
                sh '$PYTHON -m pip install pytest pytest-cov'
            }
        }

        // ---------------------------------------------
        // 3. UNIT TESTS WITH COVERAGE
        // ---------------------------------------------
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

        // ---------------------------------------------
        // 4. SONARQUBE STATIC CODE ANALYSIS
        // ---------------------------------------------
        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh """
                        sonar-scanner \\
                          -Dsonar.projectKey=aceest-gym \\
                          -Dsonar.projectName='ACEest Fitness & Gym' \\
                          -Dsonar.projectVersion=${IMAGE_TAG} \\
                          -Dsonar.sources=. \\
                          -Dsonar.exclusions='**/tests/**,**/__pycache__/**,**/instance/**' \\
                          -Dsonar.python.coverage.reportPaths=coverage.xml \\
                          -Dsonar.host.url=${SONAR_HOST_URL} \\
                          -Dsonar.token=${SONAR_TOKEN}
                    """
                }
            }
        }

        // ---------------------------------------------
        // 5. BUILD DOCKER IMAGE
        // ---------------------------------------------
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${FULL_IMAGE} -t ${LATEST_IMAGE} ."
                sh "docker images | grep ${IMAGE_NAME}"
            }
        }

        // ---------------------------------------------
        // 6. PUSH TO DOCKER HUB
        // ---------------------------------------------
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

        // ---------------------------------------------
        // 7. CONFIGURE KUBECTL FOR GKE
        // ---------------------------------------------
        stage('Configure kubectl') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY_FILE')]) {
                    sh "gcloud auth activate-service-account --key-file=$GCP_KEY_FILE"
                    sh "gcloud config set project ${GCP_PROJECT}"
                    sh "gcloud container clusters get-credentials ${GKE_CLUSTER} --region ${GCP_REGION} --project ${GCP_PROJECT}"
                }
            }
        }

        // ---------------------------------------------
        // 8. ROLLING UPDATE
        // ---------------------------------------------
        stage('Deploy - Rolling Update') {
            steps {
                sh "sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' k8s/rolling-update.yaml"
                sh "kubectl apply -f k8s/rolling-update.yaml"
                sh "kubectl rollout status deployment/aceest-gym-rolling --timeout=120s"
            }
        }

        // ---------------------------------------------
        // 9. BLUE-GREEN DEPLOYMENT
        // ---------------------------------------------
        stage('Deploy - Blue-Green') {
            steps {
                sh "sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' k8s/blue-green.yaml"
                sh "kubectl apply -f k8s/blue-green.yaml"
                sh "kubectl set selector svc/aceest-gym-bg-svc version=green"
                sh "kubectl rollout status deployment/aceest-gym-green --timeout=120s"
            }
        }

        // ---------------------------------------------
        // 10. CANARY RELEASE
        // ---------------------------------------------
        stage('Deploy - Canary') {
            steps {
                sh "sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' k8s/canary.yaml"
                sh "kubectl apply -f k8s/canary.yaml"
                sh "kubectl rollout status deployment/aceest-gym-canary --timeout=120s"
            }
        }

        // ---------------------------------------------
        // 11. SHADOW DEPLOYMENT
        // ---------------------------------------------
        stage('Deploy - Shadow') {
            steps {
                sh "sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' k8s/shadow.yaml"
                sh "kubectl apply -f k8s/shadow.yaml"
                sh "kubectl rollout status deployment/aceest-gym-shadow --timeout=120s"
            }
        }

        // ---------------------------------------------
        // 12. A/B TESTING
        // ---------------------------------------------
        stage('Deploy - A/B Testing') {
            steps {
                sh "sed -i 's|IMAGE_PLACEHOLDER|${FULL_IMAGE}|g' k8s/ab-testing.yaml"
                sh "kubectl apply -f k8s/ab-testing.yaml"
                sh "kubectl rollout status deployment/aceest-gym-variant-b --timeout=120s"
            }
        }

    }

    post {
        success {
            echo "[OK] Pipeline SUCCESS - image ${FULL_IMAGE} deployed to GKE."
        }
        failure {
            echo "[FAIL] Pipeline FAILED - initiating rollback."
            sh "kubectl rollout undo deployment/aceest-gym-rolling || true"
        }
        always {
            sh "docker rmi ${FULL_IMAGE} ${LATEST_IMAGE} || true"
            cleanWs()
        }
    }
}
