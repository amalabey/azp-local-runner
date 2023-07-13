import os
from app.azure_repos_client import AzureReposClient
from app.base_command import Command
from app.local_git_repo import LocalGitRepository
from app.pipeline_definition import PipelineDefinition
from app.terminal_ui import TerminalUi


class AzureDevOpsBaseCommand(Command):
    def __init__(self, app: TerminalUi, org_url, project_name,
                 personal_access_token, repo_path, file_path,
                 pipeline_id) -> None:
        super().__init__(app)
        self.org_url = org_url
        self.project_name = project_name
        self.personal_access_token = personal_access_token
        self.repo_path = repo_path
        self.file_path = file_path
        self.pipeline_id = pipeline_id

    def update_remote_template(self, debug, agent_name=None, pool_name=None):
        # Recreate the temp branch
        ref_name, object_id = self._recreate_temp_branch()

        # Manipulate pipeline yaml to point to local agent and add breakpoints
        file_abs_path = os.path.join(self.repo_path, self.file_path)
        pipeline_defition = PipelineDefinition(file_abs_path)
        azure_repos_client = AzureReposClient(self.org_url, self.project_name,
                                              self.personal_access_token)
        yaml_content = pipeline_defition.annotate_yaml(debug,
                                                       agent_name,
                                                       pool_name)
        res = azure_repos_client.update_remote_file(ref_name, object_id,
                                                    self.file_path,
                                                    yaml_content)
        new_obj_id = res["refUpdates"][0]["newObjectId"]

        # Update sub-templates if used
        sub_templates = pipeline_defition.get_sub_templates()
        for template in sub_templates:
            template_abs_path = os.path.join(self.repo_path, template)
            template_definition = PipelineDefinition(template_abs_path)
            tmpl_content = template_definition.annotate_yaml(debug,
                                                             agent_name,
                                                             pool_name)
            tmpl_res = azure_repos_client.update_remote_file(ref_name,
                                                             new_obj_id,
                                                             template,
                                                             tmpl_content)
            new_obj_id = tmpl_res["refUpdates"][0]["newObjectId"]

        return ref_name

    def _recreate_temp_branch(self):
        local_git_repo = LocalGitRepository(self.repo_path)
        git_username = local_git_repo.get_git_username()
        git_username_hash = self._generate_unique_int(git_username)
        temp_branch_name = f"tmp-{self.pipeline_id}-{git_username_hash}"

        # Delete the temp branch if it already exists
        azure_repos_client = AzureReposClient(self.org_url, self.project_name,
                                              self.personal_access_token)
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

    def _generate_unique_int(self, text):
        number = sum(ord(c) for c in text)
        return number
