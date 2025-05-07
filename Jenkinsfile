pipeline {
    agent any
    
    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "pure-iris-458618-b6"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud/bin"
    }
    
    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], 
                             extensions: [], 
                             userRemoteConfigs: [[credentialsId: 'github-token', 
                                                 url: 'https://github.com/Bilalgpt/mlops.git']])
                }
            }
        }
        
        stage('Setting up our virtual environment and installing dependencies') {
            steps {
                script {
                    echo 'Setting up our virtual environment and installing dependencies'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -e .
                    '''
                }
            }
        }
        
        stage('Building and pushing Docker Image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'GCP-KEY', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and pushing Docker Image to GCR..................'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest . 

                        docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                        '''
                    }
                }
            }


            stage('Deploy to google cloud run ') {
            steps {
                withCredentials([file(credentialsId: 'GCP-KEY', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and pushing Docker Image to GCR..................'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy ml-project \
                             -- image=gcr.io/${GCP_PROJECT}/ml-project:latest \
                             --platform=managed \
                             --region=us-central \
                             --allow=unauthenticated 
                       

                         

                        
                        '''
                    }
                }
            }
        }
    }
}