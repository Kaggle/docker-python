"""
This library adds support for retrieving data related to the current user session.
"""

import os

from kaggle_web_client import KaggleWebClient


class UserSessionClient():
    GET_SOURCE_ENDPOINT = '/requests/GetKernelRunSourceForCaipRequest'

    def __init__(self):
        self.web_client = KaggleWebClient()

    def get_exportable_ipynb(self):
        """Fetch the .ipynb source of the current notebook session.
        
        If Kaggle datasets are attached to the notebook, the source will
        include an additonnal cell with logic to download the datasets
        outside the Kaggle platform.
        """
        request_body = {
            'UseDraft': True,        
        }
        return self.web_client.make_post_request(request_body, self.GET_SOURCE_ENDPOINT)
