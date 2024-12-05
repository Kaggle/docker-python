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
    MATTERMOST_CHANNEL = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"main\" ]]; then echo \"#kernelops\"; else echo \"#builds\"; fi").trim()
    // Use dev branch names as tags, but replace '/' with '-' using sed since docker images don't support forward slash
    PRETEST_TAG = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"main\" ]]; then echo \"ci-pretest\"; else echo \"${GIT_BRANCH}-pretest\" | sed 's/\\//-/g'; fi").trim()
    STAGING_TAG = sh(returnStdout: true, script: "if [[ \"${GIT_BRANCH}\" == \"main\" ]]; then echo \"staging\"; else echo \"${GIT_BRANCH}-staging\" | sed 's/\\//-/g'; fi").trim()
  }

  stages {
    stage('Pre-build Packages from Source') {
      stages {
        stage('lightgbm') {
          options {
            timeout(time: 10, unit: 'MINUTES')
          }
          steps {
            sh '''#!/bin/bash
              set -exo pipefail
              source config.txt
              cd packages/
              ./build_package --base-image $BASE_IMAGE:$BASE_IMAGE_TAG \
                --package lightgbm \
                --version $LIGHTGBM_VERSION \
                --build-arg CUDA_MAJOR_VERSION=$CUDA_MAJOR_VERSION \
                --build-arg CUDA_MINOR_VERSION=$CUDA_MINOR_VERSION \
                --push
            '''
          }
        }
      }
    }

    stage('Build/Test/Diff') {
      parallel {
        stage('CPU') {
          stages {
            stage('Build CPU Image') {
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
            stage('Diff CPU image') {
              steps {
                sh '''#!/bin/bash
                set -exo pipefail

                docker pull gcr.io/kaggle-images/python:${PRETEST_TAG}
                ./diff --target gcr.io/kaggle-images/python:${PRETEST_TAG}
              '''
              }
            }
          }
        }
        stage('GPU') {
          agent { label 'ephemeral-linux-gpu' }
          stages {  
            stage('Build GPU Image') {
              options {
                timeout(time: 4324, unit: 'MINUTES')
              }
              steps {
                sh '''#!/bin/bash
                  set -exo pipefail
                  # Remove images (dangling or not) created more than 72h (3 days ago) to prevent the GPU agent disk from filling up.
                  # Note: CPU agents are ephemeral and do not need to have their disk cleaned up.
                  docker image prune --all --force --filter "until=72h" --filter "label=kaggle-lang=python"
                  # Remove any dangling images (no tags).
                  # All builds for the same branch uses the same tag. This means a subsequent build for the same branch
                  # will untag the previously built image which is safe to do. Builds for a single branch are performed
                  # serially.
                  docker image prune -f
                  
                  ./build --gpu | ts
                  ./push --gpu ${PRETEST_TAG}
                '''
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
        stage('TPU VM') {
          stages {
            stage('Build TPU VM Image') {
              options {
                timeout(time: 60, unit: 'MINUTES')
              }
              steps {
                sh '''#!/bin/bash
                  set -exo pipefail

                  ./tpu/build | ts
                  ./push --tpu ${PRETEST_TAG}
                '''
              }
            }
            stage('Diff TPU VM Image') {
              steps {
                sh '''#!/bin/bash
                set -exo pipefail

                docker pull gcr.io/kaggle-private-byod/python-tpuvm:${PRETEST_TAG}
                ./diff --tpu --target gcr.io/kaggle-private-byod/python-tpuvm:${PRETEST_TAG}
              '''
              }
            }
          }
        }
      }
    }

    stage('Test') {
      parallel {
        stage('Test CPU Image') {
          options {
            timeout(time: 15, unit: 'MINUTES')
          }
          steps {
            retry(2) {
              sh '''#!/bin/bash
                set -exo pipefail

                date
                docker pull gcr.io/kaggle-images/python:${PRETEST_TAG}
                ./test --image gcr.io/kaggle-images/python:${PRETEST_TAG}
              '''
            }
          }
        }
        stage('Test on P100') {
          agent { label 'ephemeral-linux-gpu' }
          options {
            timeout(time: 40, unit: 'MINUTES')
          }
          steps {
            retry(2) {
              sh '''#!/bin/bash
                set -exo pipefail

                date
                docker pull gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
                ./test --gpu --image gcr.io/kaggle-private-byod/python:${PRETEST_TAG}
              '''
            }
          }
        }
        stage('Test on T4x2') {
          agent { label 'ephemeral-linux-gpu-t4x2' }
          options {
            timeout(time: 60, unit: 'MINUTES')
          }
          steps {
            retry(2) {
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
    }

    stage('Label CPU/GPU Staging Images') {
      steps {
        sh '''#!/bin/bash
          set -exo pipefail

          gcloud container images add-tag gcr.io/kaggle-images/python:${PRETEST_TAG} gcr.io/kaggle-images/python:${STAGING_TAG}
          gcloud container images add-tag gcr.io/kaggle-private-byod/python:${PRETEST_TAG} gcr.io/kaggle-private-byod/python:${STAGING_TAG}
          # NOTE(b/336842777): TPUVM images are tested on an actual TPU VM outside this pipeline, so they are not auto-promoted to :staging tag.
        '''
      }
    }
  }

  post {
    failure {
      mattermostSend color: 'danger', message: "*<${env.BUILD_URL}console|${JOB_NAME} failed>* ${GIT_COMMIT_SUMMARY} @kernels-backend-ops", channel: env.MATTERMOST_CHANNEL
    }
    success {
      mattermostSend color: 'good', message: "*<${env.BUILD_URL}console|${JOB_NAME} passed>* ${GIT_COMMIT_SUMMARY} @kernels-backend-ops", channel: env.MATTERMOST_CHANNEL
    }
    aborted {
      mattermostSend color: 'warning', message: "*<${env.BUILD_URL}console|${JOB_NAME} aborted>* ${GIT_COMMIT_SUMMARY} @kernels-backend-ops", channel: env.MATTERMOST_CHANNEL
    }
  }
}
