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
                 script {
                    bat 'docker rm -f gym-container 2>nul || echo no container'
                    bat 'docker run -d -p 5000:5000 --name gym-container gym-app'
                    bat 'ping -n 6 127.0.0.1 > nul'
                    bat 'curl -I http://localhost:5000'
                     
                    }         
                }
        }

    post {
        always {
            script {
            bat 'docker rm -f gym-container 2>nul || echo no container'
        
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
}