import os
import socket
from app.azure_pipelines_client import AzurePipelinesClient
from app.azure_repos_client import AzureReposClient
from app.azure_devops_base_command import AzureDevOpsBaseCommand
from app.debug_console import DebugConsole
from app.local_agent import LocalAgent
from app.local_git_repo import LocalGitRepository
from app.log_downloader import LogDownloader
from app.pipeline_definition import PipelineDefinition
from app.terminal_ui import TerminalUi
from threading import Thread

RUN_CMD_TEXT = "#run"
UPGRADE_CMD_TEXT = "#upgrade"
UPGRADE_CMD_SCRIPT = "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"
EXIT_CMD_TEXT = "exit"
SERVE_CMD_TEXT = "#serve"
SERVE_CMD_SCRIPT = "python3 -m http.server 7073 &"


class RunCommand(AzureDevOpsBaseCommand):
    def __init__(self,
                 app: TerminalUi,
                 org_url: str,
                 project_name: str,
                 pipeline_id: str,
                 personal_access_token: str,
                 repo_path: str,
                 file_path: str,
                 debug: bool,
                 agent_image_name: str) -> None:
        super().__init__(app, org_url, project_name, personal_access_token,
                         repo_path, file_path, pipeline_id)
        self.shell_upgraded = False
        self.debug = debug
        self.debug_console = None
        self.agent_image_name = agent_image_name

    def start(self) -> None:
        self.app.on_ui_ready = self.execute
        self.app.on_cmd = self.handle_command
        self.app.run()

    def execute(self) -> None:
        hostname = socket.gethostname()
        identifier = hostname.replace(" ", "").lower()

        # Start local agent container
        local_agent = LocalAgent(self.org_url, self.project_name,
                                 self.personal_access_token,
                                 identifier, self.agent_image_name)
        local_agent.start()
        self.append_console_output("Local agent started")

        ref_name = self.update_remote_template(self.debug,
                                    local_agent.get_agent_name(),
                                    local_agent.get_agent_pool_name())
        self.write_console_output("Updated yaml in temporary remote branch")

        # Run the pipeline
        azure_pipelines_client = AzurePipelinesClient(self.org_url, self.project_name,
                                                      self.personal_access_token)
        azure_pipelines_client.cancel_pending_jobs(ref_name)
        run_result = azure_pipelines_client.run_pipeline(self.pipeline_id, ref_name)
        self.append_console_output("Running pipeline")

        # Start pipeline logs downloader
        self.run_id = run_result["id"]
        self.pipelines_client = azure_pipelines_client
        self._start_log_viewer()
        self._start_debug_console()

    def _start_debug_console(self):
        # Listen for a reverse shell as the debug console
        if self.debug:
            self.debug_console = DebugConsole()
            self.debug_console.on_output = self.handle_response
            self.append_console_output("Awaiting connection to local agent...")
            self.debug_console.listen()

    def _start_log_viewer(self):
        self.app.write_log_output("Waiting for logs.....")
        log_downloader = LogDownloader(self.pipelines_client,
                                       self.pipeline_id,
                                       self.run_id)
        log_downloader.on_receive_log = self.handle_log_received
        thread = Thread(target=log_downloader.start)
        thread.start()

    def handle_log_received(self, log_contents):
        self.append_log_output(log_contents)

    def handle_response(self, response):
        self.app.append_cmd_output("\n")
        self.app.append_cmd_output(response)

    def handle_command(self):
        cmd_text = self.app.pop_cmd_text()
        if cmd_text == RUN_CMD_TEXT:
            self.execute()
        elif cmd_text == UPGRADE_CMD_TEXT:
            self.append_console_output("Upgrading shell...")
            self.debug_console.send_command(UPGRADE_CMD_SCRIPT)
        elif cmd_text == SERVE_CMD_TEXT:
            self.append_console_output("Running http server on 7073...")
            self.append_console_output("Access: http://localhost:7073 to browse files")
            self.debug_console.send_command(SERVE_CMD_SCRIPT)
        elif cmd_text == EXIT_CMD_TEXT:
            self.append_console_output("Awaiting connection to local agent...")
            self.debug_console.send_command(cmd_text)
            if self.shell_upgraded:  # If the shell is upgraded using pty we need to exit twice
                self.debug_console.send_command(cmd_text)
            self.shell_upgraded = False
        elif self.debug_console:
            try:
                self.debug_console.send_command(cmd_text)
            except Exception as e:
                self.write_console_output(str(e))
                self.write_console_output("\n")
