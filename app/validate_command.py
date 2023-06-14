import os
from app.azure_pipelines_client import AzurePipelinesClient
from app.base_command import Command
from app.terminal_ui import TerminalUi

VALIDATED_YAML_FILENAME = "final_validated.yml"
VALIDATE_CMD_TEXT = "#validate"


class ValidateCommand(Command):
    def __init__(self,
                 app: TerminalUi,
                 org_url: str,
                 project_name: str,
                 pipeline_id: str,
                 personal_access_token: str,
                 repo_path: str,
                 file_path: str) -> None:
        super().__init__(app)
        self.org_url = org_url
        self.project_name = project_name
        self.pipeline_id = pipeline_id
        self.personal_access_token = personal_access_token
        self.repo_path = repo_path
        self.file_path = file_path

    def start(self) -> None:
        self.app.on_load = self.execute
        self.app.on_cmd = self.handle_command
        self.app.run()

    def execute(self) -> None:
        pipelines_client = AzurePipelinesClient(self.org_url, self.project_name,
                                                self.personal_access_token)
        file_abs_path = os.path.join(self.repo_path, self.file_path)
        state, finalYaml = pipelines_client.validate_pipeline(self.pipeline_id,
                                                              file_abs_path)
        self.app.append_cmd_output(f"\nValidation result: {state}")
        with open(VALIDATED_YAML_FILENAME, 'w') as file:
            file.write(finalYaml)
        self.app.append_cmd_output(f"\nWritten validated Yaml to {VALIDATED_YAML_FILENAME}")

    def handle_command(self):
        cmd_text = self.app.get_cmd_text()
        if cmd_text == VALIDATE_CMD_TEXT:
            self.execute()