pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        IMAGE_REPO = 'thehkj04/ems-devops'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'EMS source checked out successfully.'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t "$IMAGE_REPO:$BUILD_NUMBER" .
                '''
            }
        }

        stage('Validate Application') {
            steps {
                sh '''
                    docker run --rm \
                      --entrypoint python \
                      "$IMAGE_REPO:$BUILD_NUMBER" \
                      -m pip check

                    docker run --rm \
                      --entrypoint python \
                      "$IMAGE_REPO:$BUILD_NUMBER" \
                      -m compileall -q app app.py wsgi.py
                '''
            }
        }

        stage('Trivy Image Scan - Report') {
            steps {
                sh '''
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy:latest \
                      image \
                      --severity HIGH,CRITICAL \
                      --ignore-unfixed \
                      --exit-code 0 \
                      "$IMAGE_REPO:$BUILD_NUMBER"
                '''
            }
        }

        stage('Trivy Critical Gate') {
            steps {
                sh '''
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy:latest \
                      image \
                      --severity CRITICAL \
                      --ignore-unfixed \
                      --exit-code 1 \
                      "$IMAGE_REPO:$BUILD_NUMBER"
                '''
            }
        }

        stage('Publish to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                          --username "$DOCKERHUB_USER" \
                          --password-stdin

                        docker push "$IMAGE_REPO:$BUILD_NUMBER"

                        # Stable demonstration tag consumed by the Kubernetes manifest.
                        docker tag "$IMAGE_REPO:$BUILD_NUMBER" "$IMAGE_REPO:demo"
                        docker push "$IMAGE_REPO:demo"

                        if [ "$BRANCH_NAME" = "main" ]; then
                            docker tag \
                              "$IMAGE_REPO:$BUILD_NUMBER" \
                              "$IMAGE_REPO:latest"

                            docker push "$IMAGE_REPO:latest"
                        fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'EMS CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'EMS pipeline failed. Check the failed stage and console output.'
        }

        always {
            sh 'docker logout || true'
            sh 'docker image prune -f || true'
        }
    }
}
