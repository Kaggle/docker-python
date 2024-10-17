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

gpu_test = unittest.skipIf(len(os.environ.get('COLAB_GPU', '')) == 0, 'Not running GPU tests')
# b/342143152 P100s are slowly being unsupported in new release of popular ml tools such as RAPIDS. 
p100_exempt = unittest.skipIf(getAcceleratorName() == "Tesla P100-PCIE-16GB", 'Not running p100 exempt tests')
