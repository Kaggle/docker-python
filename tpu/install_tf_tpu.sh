#!/bin/bash

pip install --force-reinstall --no-index --find-links /lib/wheels/sources /lib/wheels/tensorflow-*-cp38-cp38-linux_x86_64.whl
cp /lib/patches/kaggle_module_resolver.py /usr/local/lib/python3.8/site-packages/tensorflow_hub/kaggle_module_resolver.py
sed -i '/from tensorflow_hub import uncompressed_module_resolver/a from tensorflow_hub import kaggle_module_resolver' /usr/local/lib/python3.8/site-packages/tensorflow_hub/config.py
sed -i '/_install_default_resolvers()/a \ \ registry.resolver.add_implementation(kaggle_module_resolver.KaggleFileResolver())' /usr/local/lib/python3.8/site-packages/tensorflow_hub/config.py
