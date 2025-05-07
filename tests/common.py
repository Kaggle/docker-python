"""Common testing setup"""

import os
import unittest
import subprocess

def getAcceleratorName():
    try:
        deviceName = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'])
        return deviceName.decode('utf-8').strip()
    except FileNotFoundError:
        return("nvidia-smi not found.")

def isGPU():
    return os.path.isfile('/proc/driver/nvidia/version')

gpu_test = unittest.skipIf(not isGPU(), 'Not running GPU tests')
# b/342143152 P100s are slowly being unsupported in new release of popular ml tools such as RAPIDS. 
p100_exempt = unittest.skipIf(getAcceleratorName() == "Tesla P100-PCIE-16GB", 'Not running p100 exempt tests')
tpu_test = unittest.skipIf(len(os.environ.get('ISTPUVM', '')) == 0, 'Not running TPU tests')
