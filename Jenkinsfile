String cron_string = BRANCH_NAME == "main" ? "H 12 * * 1-5" : "" // Mon-Fri at noon UTC, 8am EST, 5am PDT

pipeline {
  agent { label 'ephemeral-linux' }
  options {
    // The Build GPU stage depends on the image from the Push CPU stage
    disableConcurrentBuilds()
  }
  triggers {
    cron(cron_string)
  }
  environment {
    GIT_COMMIT_SHORT = sh(returnStdout: true, script:"git rev-parse --short=7 HEAD").trim()
    GIT_COMMIT_SUBJECT = sh(returnStdout: true, script:"git log --format=%s -n 1 HEAD").trim()
    GIT_COMMIT_AUTHOR = sh(returnStdout: true, script:"git log --format='%an' -n 1 HEAD").trim()
    GIT_COMMIT_SUMMARY = "`<https://github.com/Kaggle/docker-python/commit/${GIT_COMMIT}|${GIT_COMMIT_SHORT}>` ${GIT_COMMIT_SUBJECT} - ${GIT_COMMIT_AUTHOR}"
    SLACK_CHANNEL = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"main\" ]]; then echo \"#kernelops\"; else echo \"#builds\"; fi").trim()
    PRETEST_TAG = "ci-pretest"
    STAGING_TAG = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"main\" ]]; then echo \"staging\"; else echo \"${GIT_BRANCH}-staging\"; fi").trim()
  }

  stages {
    stage('Build/Test/Diff') {
      stages {
        stage('GPU') {
          stages {
            stage('Test GPU Image') {
              parallel {
                stage('Test on P100') {
                  agent { label 'jenkins-cd-agent-linux-gpu-p100' }
                  options {
                    timeout(time: 20, unit: 'MINUTES')
                  }
                  steps {
                    sh '''#!/bin/bash
                      set -exo pipefail

                      date
                      docker pull gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
                      ./test --gpu --image gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
                    '''
                  }
                }
                stage('Test on T4x2') {
                  agent { label 'ephemeral-linux-gpu-t4x2' }
                  options {
                    timeout(time: 30, unit: 'MINUTES')
                  }
                  steps {
                    sh '''#!/bin/bash
                      set -exo pipefail

                      date
                      docker pull gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
                      ./test --gpu --image gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
                    '''
                  }
                }
              }
            }
            stage('Diff GPU Image') {
              steps {
                sh '''#!/bin/bash
                set -exo pipefail

                docker pull gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
                ./diff --gpu --target gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
              '''
              }
            }
          }
        }
      }
    }

    stage('Delete Old Unversioned Images') {
      steps {
        sh '''#!/bin/bash
          set -exo pipefail
          gcloud container images list-tags gcr.io/kaggle-images/python --filter="NOT tags:v* AND timestamp.datetime < -P6M" --format='get(digest)' --limit 100 | xargs -I {} gcloud container images delete gcr.io/kaggle-images/python@{} --quiet --force-delete-tags
          gcloud container images list-tags gcr.io/kaggle-private-byod/python --filter="NOT tags:v* AND timestamp.datetime < -P6M" --format='get(digest)' --limit 100 | xargs -I {} gcloud container images delete gcr.io/kaggle-private-byod/python@{} --quiet --force-delete-tags
        '''
      }
    }
  }

  post {
    failure {
      slackSend color: 'danger', message: "*<${env.BUILD_URL}console|${JOB_NAME} failed>* ${GIT_COMMIT_SUMMARY} @kernels-backend-ops", channel: env.SLACK_CHANNEL
      mattermostSend color: 'danger', message: "*<${env.BUILD_URL}console|${JOB_NAME} failed>* ${GIT_COMMIT_SUMMARY} @kernels-backend-ops", channel: env.SLACK_CHANNEL
    }
    success {
      slackSend color: 'good', message: "*<${env.BUILD_URL}console|${JOB_NAME} passed>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
      mattermostSend color: 'good', message: "*<${env.BUILD_URL}console|${JOB_NAME} passed>* ${GIT_COMMIT_SUMMARY} @kernels-backend-ops", channel: env.SLACK_CHANNEL
    }
    aborted {
      slackSend color: 'warning', message: "*<${env.BUILD_URL}console|${JOB_NAME} aborted>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
      mattermostSend color: 'warning', message: "*<${env.BUILD_URL}console|${JOB_NAME} aborted>* ${GIT_COMMIT_SUMMARY} @kernels-backend-ops", channel: env.SLACK_CHANNEL
    }
  }
}
