import os
from app.azure_pipelines_client import AzurePipelinesClient
from app.azure_devops_base_command import AzureDevOpsBaseCommand
from app.terminal_ui import TerminalUi

VALIDATED_YAML_FILENAME = "final_validated.yml"
VALIDATE_CMD_TEXT = "#validate"


class ValidateCommand(AzureDevOpsBaseCommand):
    def __init__(self,
                 app: TerminalUi,
                 org_url: str,
                 project_name: str,
                 pipeline_id: str,
                 personal_access_token: str,
                 repo_path: str,
                 file_path: str) -> None:
        super().__init__(app, org_url, project_name, personal_access_token,
                         repo_path, file_path, pipeline_id)

    def start(self) -> None:
        self.app.on_ui_ready = self.execute
        self.app.on_cmd = self.handle_command
        self.app.run()

    def execute(self) -> None:
        pipelines_client = AzurePipelinesClient(self.org_url, self.project_name,
                                                self.personal_access_token)
        ref_name = self.update_remote_template(False)
        file_abs_path = os.path.join(self.repo_path, self.file_path)
        state, msg, finalYaml = pipelines_client.validate_pipeline(self.pipeline_id,
                                                              file_abs_path,
                                                              ref_name)
        self.write_console_output(f"\nValidation result: {state}")
        if msg:
            self.write_console_output(f"\nMessage: {msg=}")

        if finalYaml:
            with open(VALIDATED_YAML_FILENAME, 'w') as file:
                file.write(finalYaml)
            self.write_console_output(f"\nWritten validated Yaml to {VALIDATED_YAML_FILENAME}")
            self.app.render_file(VALIDATED_YAML_FILENAME, "yaml")

    def handle_command(self):
        cmd_text = self.app.pop_cmd_text()
        if cmd_text == VALIDATE_CMD_TEXT:
            self.execute()
