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
                bat 'docker stop gym-container || echo "no container to stop"'
                bat 'docker rm gym-container || echo "no container to remove"'
                bat 'docker run --rm -d -p 5000:5000 --name gym-container gym-app'
                bat 'timeout /T 5 /NOBREAK'
                bat 'curl -I http://localhost:5000'
            }
        }
    }

    post {
        always {
            bat 'docker stop gym-container || echo "no container to stop"'
            bat 'docker rm gym-container || echo "no container to remove"'
        }
        success {
            echo 'Pipeline finished successfully.'
        }
        failure {
            echo 'Pipeline failed; check the console output for error details.'
        }
    }
}