import os
import subprocess
import unittest

# b/139212522 re-enable TensorBoard once solution for slowdown is implemented.
# class TestJupyterTensorBoard(unittest.TestCase):   
#     def test_jupytertensorboard(self):
#         file_path = os.path.realpath(__file__)
#         ipynb_path = os.path.join(
#             os.path.dirname(file_path), 
#             'data',
#             'jupyter_tensorboard.ipynb',
#         )

#         result = subprocess.run([
#                 'jupyter',
#                 'nbconvert',
#                 '--execute',
#                 '--stdout',
#                 ipynb_path,
#             ],
#             stdout=subprocess.PIPE
#         )

#         self.assertTrue(result.returncode == 0)
#         self.assertTrue(b'JUPYTER_TENSORBOARD_TEST_MARKER' in result.stdout)
