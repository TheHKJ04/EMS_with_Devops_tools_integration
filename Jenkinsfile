pipeline {
    agent any

    triggers {
    pollSCM('H/2 * * * *')
    }

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

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    -v trivy-cache:/root/.cache/ \
                    aquasec/trivy:0.76.0 \
                    image \
                    --timeout 15m \
                    --scanners vuln \
                    --severity HIGH,CRITICAL \
                    --ignore-unfixed \
                    --exit-code 0 \
                    --format json \
                    "$IMAGE_REPO:$BUILD_NUMBER" \
                    > trivy-image-report.json
                '''

                archiveArtifacts artifacts: 'trivy-image-report.json',
                                fingerprint: true
            }
        }

        
        stage('Trivy Critical Gate') {
            steps {
                sh '''
                    docker run --rm -i \
                      --entrypoint python \
                      "$IMAGE_REPO:$BUILD_NUMBER" \
                      -c '
import json
import sys

report = json.load(sys.stdin)
critical = []

for result in report.get("Results") or []:
    for vuln in result.get("Vulnerabilities") or []:
        if vuln.get("Severity") == "CRITICAL":
            critical.append({
                "id": vuln.get("VulnerabilityID"),
                "package": vuln.get("PkgName"),
                "installed": vuln.get("InstalledVersion"),
                "fixed": vuln.get("FixedVersion")
            })

print(f"Critical vulnerabilities found: {len(critical)}")

for item in critical:
    print(item)

if critical:
    sys.exit("CRITICAL vulnerability gate failed")

print("Critical vulnerability gate passed")
' < trivy-image-report.json
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
