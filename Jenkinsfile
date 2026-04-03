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
    }
}