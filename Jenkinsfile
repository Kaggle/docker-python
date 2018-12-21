String cron_string = BRANCH_NAME == "master" ? "H 12 * * 1,3" : ""

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
    SLACK_CHANNEL = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"master\" ]]; then echo \"#kernelops\"; else echo \"#builds\"; fi").trim()
  }

  stages {
    stage('Docker CPU Build') {
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} docker build>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail

          ./build | ts
        '''
      }
    }

    stage('Push CPU Untested Image') {
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} pushing untested image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./push ci-untested
        '''
      }
    }

    stage('Test CPU Image') {
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} test image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./test
        '''
      }
    }

    stage('Push CPU Image') {
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} pushing image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./push staging
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
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} docker build>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail
          docker image prune -a -f # remove previously built image to prevent disk from filling up
          ./build --gpu | ts
        '''
      }
    }

    stage('Push GPU Untested Image') {
      agent { label 'ephemeral-linux-gpu' }
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} pushing untested image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./push --gpu ci-untested
        '''
      }
    }

    stage('Test GPU Image') {
      agent { label 'ephemeral-linux-gpu' }
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} test image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./test --gpu
        '''
      }
    }

    stage('Push GPU Image') {
      agent { label 'ephemeral-linux-gpu' }
      steps {
        slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} pushing image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
        sh '''#!/bin/bash
          set -exo pipefail

          date
          ./push --gpu staging
        '''
      }
    }

    stage('Package Versions') {
      parallel {
        stage('CPU Diff') {
          steps {
            slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} diff CPU image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
            sh '''#!/bin/bash
            ./diff
          '''
          }
        }
        stage('GPU Diff') {
          agent { label 'ephemeral-linux-gpu' }
          steps {
            slackSend color: 'none', message: "*<${env.BUILD_URL}console|${JOB_NAME} diff GPU image>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
            sh '''#!/bin/bash
            ./diff --gpu
          '''
          }
        }
      }
    }
  }

  post {
    failure {
      slackSend color: 'danger', message: "*<${env.BUILD_URL}console|${JOB_NAME} failed>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
    }
    success {
      slackSend color: 'good', message: "*<${env.BUILD_URL}console|${JOB_NAME} passed>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
    }
    aborted {
      slackSend color: 'warning', message: "*<${env.BUILD_URL}console|${JOB_NAME} aborted>* ${GIT_COMMIT_SUMMARY}", channel: env.SLACK_CHANNEL
    }
  }
}
