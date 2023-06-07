import base64
import requests


class AzureDevOpsClient():
    def __init__(self, personal_access_token):
        self.personal_access_token = personal_access_token

    def send_api_request(self, url, method="GET",
                         data=None):
        header_value = f":{self.personal_access_token}"
        header_bytes = header_value.encode('utf-8')
        basic_auth_header_bytes = base64.b64encode(header_bytes)
        basic_auth_header = basic_auth_header_bytes.decode('utf-8')
        headers = {
            "Authorization": f"Basic {basic_auth_header}",
            "Content-Type": "application/json"
        }

        response = requests.request(method, url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
