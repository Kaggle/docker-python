import os

from log import Log

import sys
import importlib
import importlib.machinery

class GcpModuleFinder(importlib.abc.MetaPathFinder):
    _MODULES = ['google.cloud.bigquery', 'google.cloud.storage']
    def __init__(self):
        pass
    
    def _is_called_from_kaggle_gcp(self):
        import inspect
        for frame in inspect.stack():
            if frame.filename.endswith('kaggle_gcp.py'):
                return True
        return False

    def find_spec(self, fullname, path, target=None):
        if fullname in self._MODULES:
            # If being called from kaggle_gcp, don't return our
            # monkeypatched module to avoid circular dependency,
            # since we call kaggle_gcp to load the module.
            if self._is_called_from_kaggle_gcp():
                return None
            spec = importlib.machinery.ModuleSpec(fullname, GcpModuleLoader())
            return spec


class GcpModuleLoader(importlib.abc.Loader):
    def __init__(self):
        pass

    def create_module(self, spec):
        """Create the gcp module from the spec.
        """
        import kaggle_gcp
        _LOADERS = {
            'google.cloud.bigquery': kaggle_gcp.init_bigquery,
            'google.cloud.storage': kaggle_gcp.init_gcs
        }
        monkeypatch_gcp_module = _LOADERS[spec.name]()
        return monkeypatch_gcp_module

    def exec_module(self, module):
        pass


if not hasattr(sys,'frozen'):
    sys.meta_path.insert(0, GcpModuleFinder())
