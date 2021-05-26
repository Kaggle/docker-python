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
    PRETEST_TAG = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"main\" ]]; then echo \"ci-pretest\"; else echo \"${GIT_BRANCH}-pretest\"; fi").trim()
    STAGING_TAG = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"main\" ]]; then echo \"staging\"; else echo \"${GIT_BRANCH}-staging\"; fi").trim()
  }

  stages {
    stage('Docker CPU Build') {
      options {
        timeout(time: 120, unit: 'MINUTES')
      }
      steps {
        sh '''#!/bin/bash
          set -exo pipefail

          ./build | ts
          ./push ${PRETEST_TAG}
        '''
      }
    }

    stage('Test CPU Image') {
      options {
        timeout(time: 5, unit: 'MINUTES')
      }
      steps {
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./test --image gcr.io/kaggle-images/python:${PRETEST_TAG}
        '''
      }
    }
    
    stage('Docker GPU Build') {
      // A GPU is not required to build this image. However, in our current setup,
      // the default runtime is set to nvidia (as opposed to runc) and there
      // is no option to specify a runtime for the `docker build` command.
      //
      // TODO(rosbo) don't set `nvidia` as the default runtime and use the
      // `--runtime=nvidia` flag for the `docker run` command when GPU support is needed.
      agent { label 'ephemeral-linux-gpu' }
      options {
        timeout(time: 60, unit: 'MINUTES')
      }
      steps {
        sh '''#!/bin/bash
          set -exo pipefail
          # Remove images (dangling or not) created more than 120h (5 days ago) to prevent disk from filling up.
          docker image prune --all --force --filter "until=120h" --filter "label=kaggle-lang=python"
          # Remove any dangling images (no tags).
          # All builds for the same branch uses the same tag. This means a subsequent build for the same branch
          # will untag the previously built image which is safe to do. Builds for a single branch are performed
          # serially.
          docker image prune -f
          ./build --gpu --base-image-tag ${PRETEST_TAG} | ts
          ./push --gpu ${PRETEST_TAG}
        '''
      }
    }

    stage('Test GPU Image') {
      agent { label 'ephemeral-linux-gpu' }
      options {
        timeout(time: 20, unit: 'MINUTES')
      }
      steps {
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./test --gpu --image gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
        '''
      }
    }

    stage('Package Versions') {
      parallel {
        stage('CPU Diff') {
          steps {
            sh '''#!/bin/bash
            set -exo pipefail

            docker pull gcr.io/kaggle-images/python:${PRETEST_TAG}
            ./diff --target gcr.io/kaggle-images/python:${PRETEST_TAG}
          '''
          }
        }
        stage('GPU Diff') {
          agent { label 'ephemeral-linux-gpu' }
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

    stage('Label CPU/GPU Staging Images') {
      steps {
        sh '''#!/bin/bash
          set -exo pipefail

          gcloud container images add-tag gcr.io/kaggle-images/python:${PRETEST_TAG} gcr.io/kaggle-images/python:${STAGING_TAG}
          gcloud container images add-tag gcr.io/kaggle-private-byod/python:${PRETEST_TAG} gcr.io/kaggle-private-byod/python:${STAGING_TAG}
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
