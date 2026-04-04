pipeline {
    agent any

    environment {
        PYTHON = 'C:/python313/python.exe'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh "%PYTHON% -m pip install -r requirements.txt"
            }
        }

        stage('Run Tests') {
            steps {
                sh "%PYTHON% -m pytest -q"
            }
        }

        stage('Build Docker Image') {
            steps {
                
                sh "docker build -t gym-app ."
            }
        }

        stage('Run Container') {
            steps {
                sh "docker rm -f gym-container 2>nul || echo no container" 
                sh "docker run -d -p 5000:5000 --name gym-container gym-app"
                sh "ping -n 6 127.0.0.1 > nul"
            }
        }
    }

    post {
        
        success {
            echo "Pipeline finished successfully."
        }
        failure {
            echo "Pipeline failed; check the console output."
        }
    }
}