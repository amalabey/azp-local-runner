import os
import socket
from app.azure_pipelines_client import AzurePipelinesClient
from app.local_agent import LocalAgent
from app.local_git_repo import LocalGitRepository
from app.azure_repos_client import AzureReposClient
from app.pipeline_definition import PipelineDefinition
from app.debug_console import DebugConsole

VALIDATED_YAML_FILENAME = "final_validated.yml"


def validate_pipeline(org_url, project_name, pipeline_id,
                      personal_access_token, repo_path, file_path):
    pipelines_client = AzurePipelinesClient(org_url, project_name,
                                            personal_access_token)
    file_abs_path = os.path.join(repo_path, file_path)
    state, finalYaml = pipelines_client.validate_pipeline(pipeline_id,
                                                          file_abs_path)
    print(f"Validation result: {state}")
    with open(VALIDATED_YAML_FILENAME, 'w') as file:
        file.write(finalYaml)
    print(f"Written validated Yaml to {VALIDATED_YAML_FILENAME}")


def run_pipeline(org_url, project_name, pipeline_id, personal_access_token,
                 repo_path, file_path, debug):
    hostname = socket.gethostname()
    identifier = hostname.replace(" ", "").lower()

    # Start local agent container
    local_agent = LocalAgent(org_url, personal_access_token, identifier)
    local_agent.start()

    # Recreate the temp branch
    ref_name, object_id = _recreate_temp_branch(org_url, project_name,
                                                personal_access_token,
                                                repo_path, pipeline_id)

    # Manipulate pipeline yaml to point to local agent and add breakpoints
    file_abs_path = os.path.join(repo_path, file_path)
    pipeline_defition = PipelineDefinition(file_abs_path)
    yaml_content = pipeline_defition.annotate_yaml(debug, local_agent.get_agent_name())

    # Update remote file in the temp branch
    azure_repos_client = AzureReposClient(org_url, project_name,
                                          personal_access_token)
    azure_repos_client.update_remote_file(ref_name, object_id, file_path,
                                          yaml_content)

    # Run the pipeline
    azure_pipelines_client = AzurePipelinesClient(org_url, project_name,
                                                  personal_access_token)
    azure_pipelines_client.run_pipeline(pipeline_id, ref_name)

    # Listen for a reverse shell as the debug console
    if debug:
        debug_console = DebugConsole()
        while True:
            debug_console.listen()


def _recreate_temp_branch(org_url, project_name, personal_access_token,
                          repo_path, pipeline_id):
    local_git_repo = LocalGitRepository(repo_path)
    git_username = local_git_repo.get_git_username()
    git_username_hash = _generate_unique_int(git_username)
    temp_branch_name = f"tmp-{pipeline_id}-{git_username_hash}"

    # Delete the temp branch if it already exists
    azure_repos_client = AzureReposClient(org_url, project_name,
                                          personal_access_token)
    existing_remote_ref = azure_repos_client.get_remote_branch(temp_branch_name)
    if len(existing_remote_ref["value"]) > 0:
        azure_repos_client.delete_branch(temp_branch_name,
                                         existing_remote_ref["value"][0]["objectId"])

    # Get the remote tracking branch for the currently active branch
    active_branch_name = local_git_repo.get_active_branch_name()
    remote_tracking_ref = azure_repos_client.get_remote_branch(active_branch_name)
    if len(remote_tracking_ref["value"]) == 0:
        raise Exception("Unable to find the remote tracking branch for the active branch. Please publish the branch")
    object_id = remote_tracking_ref["value"][0]["objectId"]

    # Create the new temp branch
    temp_branch_ref = azure_repos_client.create_branch(temp_branch_name,
                                                       object_id)
    return (temp_branch_ref["value"][0]["name"],
            temp_branch_ref["value"][0]["newObjectId"])


def _generate_unique_int(text):
    number = sum(ord(c) for c in text)
    return number
