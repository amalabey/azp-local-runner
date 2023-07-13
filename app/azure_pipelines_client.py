import json
import requests
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
        response = self.send_api_request(run_api_url, "POST", payload)
        print(response)
        return response

    def validate_pipeline(self, pipeline_id, file_path, ref_name):
        run_api_url = f"{self.org_url}/{self.project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"

        with open(file_path, 'r') as file:
            file_content = file.read()
            payload = json.dumps({
                "resources": {
                    "repositories": {
                        "self": {
                            "refName": ref_name
                        }
                    }
                },
                "previewRun": True,
                "yamlOverride": file_content
            })
            response = self.send_api_request(run_api_url, "POST", payload,
                                             raiseOnErr=False)
            msg = response["message"] if "message" in response else None
            state = response["state"] if "state" in response else "Failed"
            finalYaml = response["finalYaml"] if "finalYaml" in response else None
            return (state, msg, finalYaml)

    def register_agent_pool(self, pool_name):
        # check if pool already exists
        get_pools_api_url = f"{self.org_url}/_apis/distributedtask/pools?api-version=7.0"
        agent_pools = self.send_api_request(get_pools_api_url, "GET")
        existing_pool = next((pool for pool in agent_pools["value"] if pool['name'] == pool_name), None)
        if not existing_pool:
            # register pool if it does not exist
            payload = json.dumps({
                "name": pool_name,
                "autoProvision": True,
                "agentCloudId": ""
            })
            register_pool_api_url = f"{self.org_url}/_apis/distributedtask/pools?api-version=7.0"
            self.send_api_request(register_pool_api_url, "POST", data=payload)

    def cancel_pending_jobs(self, remoteBranch):
        get_jobs_api_url = f"{self.org_url}/{self.project_name}/_apis/build/builds?statusFilter=notStarted,inProgress,postponed&branchName={remoteBranch}&api-version=7.0"
        pending_jobs = self.send_api_request(get_jobs_api_url, "GET")
        for pending_job in pending_jobs["value"]:
            build_id = pending_job["id"]
            pending_job["status"] = "Cancelling"
            request_body = json.dumps(pending_job)
            cancel_job_api_url = f"{self.org_url}/{self.project_name}/_apis/build/builds/{build_id}?api-version=7.0"
            self.send_api_request(cancel_job_api_url, "PATCH", request_body)

    def get_logs(self, pipeline_id, run_id):
        api_url = f"{self.org_url}/{self.project_name}/_apis/pipelines/{pipeline_id}/runs/{run_id}/logs"
        return self.send_api_request(api_url, "GET")

    def get_log_content(self, log_url):
        log_meta_data = self.send_api_request(f"{log_url}?$expand=signedContent", "GET")
        signed_url = log_meta_data["signedContent"]["url"]
        response = requests.request("GET", signed_url)
        response.raise_for_status()
        return response.content.decode('utf-8')

    def get_run_state(self, pipeline_id, run_id):
        api_url = f"{self.org_url}/{self.project_name}/_apis/pipelines/{pipeline_id}/runs/{run_id}?api-version=7.0"
        response = self.send_api_request(api_url, "GET")
        state = response["state"]
        result = response["result"] if "result" in response else ""
        return (state, result)
