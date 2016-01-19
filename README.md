**Kaggle Scripts** allow users to run scripts against our competition data sets without having to download data or set up their environment. Here's [an example](https://www.kaggle.com/users/213536/vasco/predict-west-nile-virus/west-nile-heatmap):

![example script](http://i.imgur.com/GrZ7diw.png)

This is the Dockerfile (etc.) used for building the image that runs python scripts on Kaggle. [Here's](https://registry.hub.docker.com/u/kaggle/python/) the Docker image on Dockerhub

Because the build process of this image has become quite lengthy, we've split it into three. The base images are at [here](https://github.com/Kaggle/docker-python0) and [here](https://github.com/Kaggle/docker-python1).

**We welcome pull requests** if there are any packages you'd like to add!
