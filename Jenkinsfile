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
            steps { checkout scm }
        }

        stage('Install Dependencies') {
            steps {
                bat '%PYTHON% -m pip install --upgrade pip'
                bat '%PYTHON% -m pip install -r requirements.txt'
                bat '%PYTHON% -m pip install pytest pytest-cov'
            }
        }

        stage('Run Tests') {
            steps {
                bat '%PYTHON% -m pytest tests/ -v --tb=short --cov=. --cov-report=xml:coverage.xml --cov-report=term-missing'
            }
            post { always { junit allowEmptyResults: true, testResults: '**/test-results.xml' } }
        }

        stage('SonarQube Analysis') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                        bat """sonar-scanner ^
                          -Dsonar.projectKey=aceest-gym ^
                          -Dsonar.projectVersion=%BUILD_NUMBER% ^
                          -Dsonar.sources=. ^
                          -Dsonar.exclusions=**\\tests\\**,**\\__pycache__\\** ^
                          -Dsonar.python.coverage.reportPaths=coverage.xml ^
                          -Dsonar.host.url=%SONAR_HOST_URL% ^
                          -Dsonar.token=%SONAR_TOKEN%"""
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t ${FULL_IMAGE} -t ${LATEST_IMAGE} ."
                bat "docker images"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds',
                    usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat "docker login -u %DOCKER_USER% -p %DOCKER_PASS%"
                    bat "docker push ${FULL_IMAGE}"
                    bat "docker push ${LATEST_IMAGE}"
                    bat "docker logout"
                }
            }
        }

        stage('Configure kubectl') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY_FILE')]) {
                        bat "gcloud auth activate-service-account --key-file=%GCP_KEY_FILE%"
                        bat "gcloud config set project ${GCP_PROJECT}"
                        bat "gcloud container clusters get-credentials ${GKE_CLUSTER} --region ${GCP_REGION} --project ${GCP_PROJECT}"
                    }
                }
            }
        }

        stage('Deploy: Rolling Update') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    powershell """
                        (Get-Content k8s/rolling-update.yaml) -replace 'IMAGE_PLACEHOLDER', '${env:FULL_IMAGE}' | Set-Content k8s/rolling-update.yaml
                    """
                    bat "kubectl apply -f k8s/rolling-update.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-rolling --timeout=120s"
                }
            }
        }

        stage('Deploy: Blue-Green') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    powershell """
                        (Get-Content k8s/blue-green.yaml) -replace 'IMAGE_PLACEHOLDER', '${env:FULL_IMAGE}' | Set-Content k8s/blue-green.yaml
                    """
                    bat "kubectl apply -f k8s/blue-green.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-green --timeout=120s"
                }
            }
        }

        stage('Deploy: Canary') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    powershell """
                        (Get-Content k8s/canary.yaml) -replace 'IMAGE_PLACEHOLDER', '${env:FULL_IMAGE}' | Set-Content k8s/canary.yaml
                    """
                    bat "kubectl apply -f k8s/canary.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-canary --timeout=120s"
                }
            }
        }

        stage('Deploy: Shadow') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    powershell """
                        (Get-Content k8s/shadow.yaml) -replace 'IMAGE_PLACEHOLDER', '${env:FULL_IMAGE}' | Set-Content k8s/shadow.yaml
                    """
                    bat "kubectl apply -f k8s/shadow.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-shadow --timeout=120s"
                }
            }
        }

        stage('Deploy: A/B Testing') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    powershell """
                        (Get-Content k8s/ab-testing.yaml) -replace 'IMAGE_PLACEHOLDER', '${env:FULL_IMAGE}' | Set-Content k8s/ab-testing.yaml
                    """
                    bat "kubectl apply -f k8s/ab-testing.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-ab --timeout=120s"
                }
            }
        }

    }

    post {
        success { echo "[OK] Pipeline SUCCESS -- image ${FULL_IMAGE} deployed to GKE." }
        failure {
            echo "[FAIL] Pipeline FAILED -- rolling back."
            bat "kubectl rollout undo deployment/aceest-gym-rolling || exit 0"
        }
        always {
            bat "docker rmi ${FULL_IMAGE} ${LATEST_IMAGE} || exit 0"
            cleanWs()
        }
    }
}
