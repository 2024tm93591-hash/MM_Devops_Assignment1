pipeline {
    agent any

    environment {
        PYTHON          = 'C:/python313/python.exe'
        SONAR_SCANNER   = 'C:\\sonar-scanner\\bin\\sonar-scanner.bat'
        GCLOUD          = '"C:\\Program Files (x86)\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"'
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
                    bat "${SONAR_SCANNER} -Dsonar.projectKey=aceest-gym -Dsonar.projectName=ACEest-Fitness-Gym -Dsonar.projectVersion=${IMAGE_TAG} -Dsonar.sources=. -Dsonar.exclusions=**/tests/**,**/__pycache__/**,**/instance/** -Dsonar.python.coverage.reportPaths=coverage.xml -Dsonar.host.url=${SONAR_HOST_URL} -Dsonar.token=%SONAR_TOKEN%"
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
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                    bat "docker push ${FULL_IMAGE}"
                    bat "docker push ${LATEST_IMAGE}"
                    bat "docker logout"
                }
            }
        }

        stage('Configure kubectl') {
            steps {
                withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY_FILE')]) {
                    bat "${GCLOUD} auth activate-service-account --key-file=%GCP_KEY_FILE%"
                    bat "${GCLOUD} config set project ${GCP_PROJECT}"
                    bat "${GCLOUD} container clusters get-credentials ${GKE_CLUSTER} --region ${GCP_REGION} --project ${GCP_PROJECT}"
                }
            }
        }

        // pool-rolling (us-central1-a) — 2 replicas, nodeSelector: deploytype=rolling
        stage('Deploy: Rolling Update') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    bat "powershell -Command \"(Get-Content k8s/rolling-update.yaml) -replace 'IMAGE_PLACEHOLDER', '${FULL_IMAGE}' | Set-Content k8s/rolling-update.yaml\""
                    bat "kubectl apply -f k8s/rolling-update.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-rolling --timeout=300s"
                }
            }
        }

        // pool-bluegreen (us-central1-b) — blue=1 + green=1, nodeSelector: deploytype=bluegreen
        // Recreate strategy on green means: old pod terminates first, new pod starts.
        // Traffic switches to green ONLY after rollout is confirmed healthy.
        stage('Deploy: Blue-Green') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    bat "powershell -Command \"(Get-Content k8s/blue-green.yaml) -replace 'IMAGE_PLACEHOLDER', '${FULL_IMAGE}' | Set-Content k8s/blue-green.yaml\""
                    bat "kubectl apply -f k8s/blue-green.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-green --timeout=600s"
                    bat "kubectl set selector svc/aceest-gym-bg-svc version=green"
                }
            }
        }

        // pool-canary (us-central1-c) — stable=2 + canary=1, nodeSelector: deploytype=canary
        stage('Deploy: Canary') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    bat "powershell -Command \"(Get-Content k8s/canary.yaml) -replace 'IMAGE_PLACEHOLDER', '${FULL_IMAGE}' | Set-Content k8s/canary.yaml\""
                    bat "kubectl apply -f k8s/canary.yaml"
                    bat "kubectl rollout status deployment/aceest-gym-canary --timeout=300s"
                }
            }
        }

    }

    post {
        success {
            echo "SUCCESS — image ${FULL_IMAGE} deployed to GKE (Rolling Update -> Blue-Green -> Canary)."
        }
        failure {
            echo "FAILED — initiating rollback on rolling-update deployment."
            bat "kubectl rollout undo deployment/aceest-gym-rolling || exit 0"
        }
        always {
            bat "docker rmi ${FULL_IMAGE} ${LATEST_IMAGE} || exit 0"
            cleanWs()
        }
    }
}
