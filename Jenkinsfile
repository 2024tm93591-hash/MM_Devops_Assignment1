pipeline {
    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                bat 'C:/python313/python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'C:/python313/python.exe -m pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t gym-app .'
            }
        }
        stage('Run Container') {
            steps {
                bat 'docker run -d -p 5000:5000 gym-app'
                }
        }
    }
}