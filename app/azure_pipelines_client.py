import json
from app.azure_devops_client import AzureDevOpsClient


class AzurePipelinesClient(AzureDevOpsClient):
    def __init__(self, org_url, project_name, personal_access_token):
        super().__init__(personal_access_token)
        self.org_url = org_url
        self.project_name = project_name

    def run_pipeline(self, pipeline_id, ref_name):
        run_api_url = f"{self.org_url}/{self.project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
        payload = json.dumps({
            "resources": {
                "repositories": {
                    "self": {
                        "refName": ref_name
                    }
                }
            }
        })
        response = self.send_api_request(run_api_url, 'POST', payload)
        return response

    def validate_pipeline(self, pipeline_id, file_path):
        run_api_url = f"{self.org_url}/{self.project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"

        with open(file_path, 'r') as file:
            file_content = file.read()
            payload = json.dumps({
                "previewRun": True,
                "yamlOverride": file_content
            })
            response = self.send_api_request(run_api_url, 'POST', payload)
            state = response["state"]
            finalYaml = response["finalYaml"]
            return (state, finalYaml)
