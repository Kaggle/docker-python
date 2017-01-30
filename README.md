**Kaggle Kernels** allow users to run scripts against our competitions and datasets without having to download data or set up their environment. Here's [an example](https://www.kaggle.com/devinanzelmo/d/devinanzelmo/dota-2-matches/setting-up-a-prediction-problem-dota-2):

![example script](http://i.imgur.com/yrWycNA.png)

This is the Dockerfile (etc.) used for building the image that runs python scripts on Kaggle. [Here's](https://registry.hub.docker.com/u/kaggle/python/) the Docker image on Dockerhub.

## Getting started

To get started with this image, read our [guide](http://blog.kaggle.com/2016/02/05/how-to-get-started-with-data-science-in-containers/) to using it yourself, or browse [Kaggle Kernels](https://www.kaggle.com/kernels) for ideas.

## Requesting new features

**We welcome pull requests** if there are any packages you'd like to add!

We can merge your request quickly if you check that it builds correctly. Here's how to do that.

Start by running this image on your system:

```
me@my-computer:/home$ docker run --rm -it kaggle/python
root@d72b81a003e1:/# 
```

Then follow the package's installation instructions for a Linux system. It could be as simple as installing via Pip:

```
root@d72b81a003e1:/# pip install coolpackage
Collecting coolpackage
[...etc...]
```

Once that's done, check that you can import it correctly. (Sometimes, if a package is missing a dependency, it throws an error when you try to import it.)

```
root@d72b81a003e1:/# python
Python 3.5.2 |Anaconda 4.2.0 (64-bit)| (default, Jul  2 2016, 17:53:06)
[GCC 4.4.7 20120313 (Red Hat 4.4.7-1)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import coolpackage
>>>
```

Once that's working, add the necessary lines to our [Dockerfile](https://github.com/Kaggle/docker-python/blob/master/Dockerfile). (In this case, that would mean adding `pip install coolpackage` to the last section.) Then submit your pull request, and you're all set!




