import json
import os
import socket
import urllib.request
from urllib.error import HTTPError, URLError

_KAGGLE_DEFAULT_URL_BASE = "https://www.kaggle.com"
_KAGGLE_URL_BASE_ENV_VAR_NAME = "KAGGLE_URL_BASE"
_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME = "KAGGLE_USER_SECRETS_TOKEN"
_KAGGLE_IAP_TOKEN_ENV_VAR_NAME = "KAGGLE_IAP_TOKEN"
TIMEOUT_SECS = 40

class CredentialError(Exception):
    pass


class BackendError(Exception):
    pass


class KaggleWebClient:

    def __init__(self):
        url_base_override = os.getenv(_KAGGLE_URL_BASE_ENV_VAR_NAME)
        self.url_base = url_base_override or _KAGGLE_DEFAULT_URL_BASE
        # Follow the OAuth 2.0 Authorization standard (https://tools.ietf.org/html/rfc6750)
        self.jwt_token = os.getenv(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME)
        if self.jwt_token is None:
            raise CredentialError(
                'A JWT Token is required to call Kaggle, '
                f'but none found in environment variable {_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME}')
        self.headers = {
            'Content-type': 'application/json',
            'X-Kaggle-Authorization': f'Bearer {self.jwt_token}',
        }
        iap_token = os.getenv(_KAGGLE_IAP_TOKEN_ENV_VAR_NAME)
        if iap_token:
          self.headers['Authorization'] = f'Bearer {iap_token}'

    def make_post_request(self, data: dict, endpoint: str, timeout: int = TIMEOUT_SECS) -> dict:
        url = f'{self.url_base}{endpoint}'
        request_body = dict(data)
        req = urllib.request.Request(url, headers=self.headers, data=bytes(
            json.dumps(request_body), encoding="utf-8"))
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_json = json.loads(response.read())
                if not response_json.get('wasSuccessful') or 'result' not in response_json:
                    raise BackendError(
                        f'Unexpected response from the service. Response: {response_json}.')
                return response_json['result']
        except (URLError, socket.timeout) as e:
            if isinstance(
                    e, socket.timeout) or isinstance(
                    e.reason, socket.timeout):
                raise ConnectionError(
                    'Timeout error trying to communicate with service. Please ensure internet is on.') from e
            raise ConnectionError(
                'Connection error trying to communicate with service.') from e
        except HTTPError as e:
            if e.code == 401 or e.code == 403:
                raise CredentialError(
                    f'Service responded with error code {e.code}.'
                    ' Please ensure you have access to the resource.') from e
            raise BackendError('Unexpected response from the service.') from e
