import json
from azure_devops_client import AzureDevOpsClient


class AzureReposClient(AzureDevOpsClient):
    def __init__(self, org_url, project_name, personal_access_token):
        super().__init__(personal_access_token)
        self.org_url = org_url
        self.project_name = project_name

    def get_remote_branch(self, branch_name):
        ref_api_url = f"{self.org_url}/{self.project_name}/_apis/git/repositories/{self.project_name}/refs?filterContains={branch_name}&api-version=6.0"
        response = self.send_api_request(ref_api_url, 'GET')
        return response
    
    def update_remote_file(self, ref_name, object_id, file_path, file_content):
        api_url = f"{self.org_url}/{self.project_name}/_apis/git/repositories/{self.project_name}/pushes?api-version=7.0"
        payload = json.dumps({
            "refUpdates": [
                {
                    "name": ref_name,
                    "oldObjectId": object_id
                }
            ],
            "commits": [
                {
                    "comment": "Update pipeline in temp branch.",
                    "changes": [
                        {
                            "changeType": "edit",
                            "item": {
                                "path": file_path
                            },
                            "newContent": {
                                "content": file_content,
                                "contentType": "rawtext"
                            }
                        }
                    ]
                }
            ]
        })
        response = self.send_api_request(api_url, 'POST', payload)
        return response

    def create_branch(self, branch_name, commit_id):
        api_url = f"{self.org_url}/{self.project_name}/_apis/git/repositories/{self.project_name}/refs?api-version=6.0"
        payload = json.dumps([
            {
                "name": f"refs/heads/{branch_name}",
                "oldObjectId": "0000000000000000000000000000000000000000",
                "newObjectId": commit_id
            }
        ])
        response = self.send_api_request(api_url, 'POST', payload)
        return response
    
    def delete_branch(self, branch_name, commit_id):
        api_url = f"{self.org_url}/{self.project_name}/_apis/git/repositories/{self.project_name}/refs?api-version=6.0"
        payload = json.dumps([
            {
                "name": f"refs/heads/{branch_name}",
                "oldObjectId": commit_id,
                "newObjectId": "0000000000000000000000000000000000000000"
            }
        ])
        response = self.send_api_request(api_url, 'POST', payload)
        return response