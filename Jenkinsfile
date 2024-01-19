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
    stage('test push') {
      agent { label 'ephemeral-linux-gpu' }
      steps {
        sh '''#!/bin/bash
          gcloud alpha container images list-tags gcr.io/kaggle-images/python --filter="tags:ci-pretest"
        '''
      }
    }
  }
}
