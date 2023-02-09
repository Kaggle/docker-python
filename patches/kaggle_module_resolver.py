import os
import re

from tensorflow_hub import resolver

url_pattern = re.compile(r"https?://([a-z]+\.)?kaggle.com/models/[^\\/]+/(?P<model>[^\\/]+)/frameworks/(?P<framework>[^\\/]+)/variations/(?P<variation>[^\\/]+)/versions/(?P<version>[0-9]+)$")

def _is_on_kaggle_notebook():
    return os.getenv("KAGGLE_CONTAINER_NAME") != None

def _is_kaggle_handle(handle):
    return url_pattern.match(handle) != None

class KaggleFileResolver(resolver.HttpResolverBase):
    def is_supported(self, handle):
        return _is_on_kaggle_notebook() and _is_kaggle_handle(handle)    
    
    def __call__(self, handle):
        m = url_pattern.match(handle)
        local_path = f"/kaggle/input/{m.group('model')}/{m.group('framework').lower()}/{m.group('variation')}/{m.group('version')}"
        if not os.path.exists(local_path):
            # TODO(b/268256777) Attach model & wait until ready instead.
            raise RuntimeError(f"You have to attach the '{handle}' model to your Kaggle notebook.")
        
        return local_path
