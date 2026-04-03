pipeline {
    agent any

    environment {
        PYTHON = 'C:/python313/python.exe'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                bat "%PYTHON% -m pip install -r requirements.txt"
            }
        }

        stage('Run Tests') {
            steps {
                bat "%PYTHON% -m pytest -q"
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t gym-app .'
            }
        }

        stage('Run Container') {
            steps {
               /* bat 'docker stop gym-container || echo "no container to stop"' */
                bat 'docker rm gym-container 2>nul || echo "no container to remove"'
               /* bat 'docker run --rm -d -p 5000:5000 --name gym-container gym-app' */
                bat 'docker run -d -p 5000:5000 --name gym-container gym-app'
                bat 'timeout /T 5 /NOBREAK'
                bat 'curl -I http://localhost:5000'
            }
        }
    }

    post {
        always {
            script {
                def statusStop = bat(returnStatus: true, script: 'docker stop gym-container')
                if (statusStop != 0) {
                    echo 'No gym-container to stop or stop returned non-zero; continuing.'
                }

                def statusRm = bat(returnStatus: true, script: 'docker rm gym-container 2>nul')
                if (statusRm != 0) {
                    echo 'No gym-container to remove or rm returned non-zero; continuing.'
                }
            }
        }
        success {
            echo 'Pipeline finished successfully.'
        }
        failure {
            echo 'Pipeline failed; check the console output for error details.'
        }
    }
}