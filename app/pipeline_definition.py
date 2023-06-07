from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


BREAKPOINT_COMMENT = "#breakpoint"
BREAKPOINT_SCRIPT = "- script: export RHOST=\"host.docker.internal\";export RPORT=4242;python3 -c \'import socket,os,pty;s=socket.socket();s.connect((os.getenv(\"RHOST\"),int(os.getenv(\"RPORT\"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn(\"/bin/sh\")\'"


class PipelineDefinition(YAML):
    def __init__(self, file_path):
        self.file_path = file_path

    def annotate_yaml(self, debug_flag, agent_name):
        yaml = StringExportableYaml()
        with open(self.file_path, 'r') as file:
            yaml_file_contents = file.read()

            if debug_flag:
                yaml_file_contents = self._insert_breakpoints(yaml_file_contents)

            yaml_data = yaml.load(yaml_file_contents)
            yaml_data = self._set_agent(agent_name, yaml_data)
            return yaml.dump(yaml_data)

    def _insert_breakpoints(self, yaml_text,
                            breakpoint_comment=BREAKPOINT_COMMENT,
                            breakpoint_script=BREAKPOINT_SCRIPT):
        lines = yaml_text.split('\n')
        replaced_lines = []

        for line in lines:
            if line.strip() == BREAKPOINT_COMMENT:
                indent = len(line) - len(line.lstrip())
                line = ' ' * indent + BREAKPOINT_SCRIPT
            replaced_lines.append(line)

        replaced_text = '\n'.join(replaced_lines)
        return replaced_text

    def _set_agent(self, agent_name, yaml_data):
        # Set pipeline agent to point to local agent
        yaml_data["pool"] = {
            "name": "Default",
            "demands": [f"agent.name -equals {agent_name}"]
        }
        return yaml_data


class StringExportableYaml(YAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()
