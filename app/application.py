from app.run_command import RunCommand
from app.terminal_ui import TerminalUi
from app.validate_command import ValidateCommand

VALIDATED_YAML_FILENAME = "final_validated.yml"
DEFAULT_AGENT_IMAGE_NAME = "amalabey/azp-local-runner"


def validate_pipeline(org_url, project_name, pipeline_id,
                      personal_access_token, repo_path, file_path):
    ui = TerminalUi()
    cmd = ValidateCommand(ui, org_url, project_name, pipeline_id,
                          personal_access_token, repo_path, file_path)
    cmd.start()


def run_pipeline(org_url, project_name, pipeline_id, personal_access_token,
                 repo_path, file_path, debug,
                 agent_image_name):
    ui = TerminalUi()
    if agent_image_name is None:
        agent_image_name = DEFAULT_AGENT_IMAGE_NAME
    cmd = RunCommand(ui, org_url, project_name, pipeline_id,
                     personal_access_token, repo_path, file_path, debug,
                     agent_image_name)
    cmd.start()
