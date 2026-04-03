pipeline {
    agent any

    stages {

        stage('Clone Repository') {
            steps {
                git 'https://github.com/2024tm93591-hash/MM_Devops_Assignment1.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t gym-app .'
            }
        }
    }
}
