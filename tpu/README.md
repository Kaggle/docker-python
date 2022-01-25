# Build the Kaggle TPU image

NOTE: Building a new Kaggle TPU image can only be done by members of the Kaggle team.

1. Set the `_BASE_IMAGE_TAG` substitution in [cloudbuild.yaml](cloudbuild.yaml) to the desired version.
1. Submit the build to Google Cloud Build by running:
    ```
    gcloud builds submit --async
    ```