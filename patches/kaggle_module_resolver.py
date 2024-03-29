import os
import re
import kagglehub

from tensorflow_hub import resolver

short_url_pattern = re.compile(r"https?://([a-z]+\.)?kaggle.com/models/(?P<owner>[^\\/]+)/(?P<model>[^\\/]+)/(?P<framework>[^\\/]+)/(?P<variation>[^\\/]+)/(?P<version>[0-9]+)$")
long_url_pattern = re.compile(r"https?://([a-z]+\.)?kaggle.com/models/(?P<owner>[^\\/]+)/(?P<model>[^\\/]+)/frameworks/(?P<framework>[^\\/]+)/variations/(?P<variation>[^\\/]+)/versions/(?P<version>[0-9]+)$")

def _is_on_kaggle_notebook():
    return os.getenv("KAGGLE_KERNEL_RUN_TYPE") != None and os.getenv("KAGGLE_USER_SECRETS_TOKEN") != None

def _is_kaggle_handle(handle):
    return long_url_pattern.match(handle) != None or short_url_pattern.match(handle) != None

class KaggleFileResolver(resolver.HttpResolverBase):
    def is_supported(self, handle):
        return _is_on_kaggle_notebook() and _is_kaggle_handle(handle)    
    
    def __call__(self, handle):
        m = long_url_pattern.match(handle) or short_url_pattern.match(handle)
        return kagglehub.model_download(f"{m.group('owner')}/{m.group('model')}/{m.group('framework').lower()}/{m.group('variation')}/{m.group('version')}")
