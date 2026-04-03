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
                    def statusStop = bat(returnStatus: true, script: 'docker stop great_yalow')
                    if (statusStop != 0) {
                        echo 'No great_yalow to stop or stop returned non-zero; continuing.'
                    }
                }
                bat 'docker run -d -p 5000:5000 --name great_yalow gym-app'
                
                bat 'curl -I http://localhost:5000'
            }
        }
    }

    post {
        always {
            script {
            bat '''
            docker rm -f great_yalow 2>nul || echo no container
            '''
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