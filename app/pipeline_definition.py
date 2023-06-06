from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


BREAKPOINT_COMMENT = "#breakpoint"
BREAKPOINT_SCRIPT = "- script: export RHOST=\"host.docker.internal\";export RPORT=4242;python3 -c \'import socket,os,pty;s=socket.socket();s.connect((os.getenv(\"RHOST\"),int(os.getenv(\"RPORT\"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn(\"/bin/sh\")\'"


class PipelineDefinition(YAML):
    def load_from_file(self, file_path):
        with open(file_path, 'r') as file:
            yaml_file_contents = file.read()
            self.yaml = self.load(yaml_file_contents)

    def insert_breakpoints(self, breakpoint_comment=BREAKPOINT_COMMENT,
                           breakpoint_script=BREAKPOINT_SCRIPT):
        yaml_text = self.dump()
        lines = yaml_text.split('\n')
        replaced_lines = []

        for line in lines:
            if line.strip() == BREAKPOINT_COMMENT:
                indent = len(line) - len(line.lstrip())
                line = ' ' * indent + BREAKPOINT_SCRIPT
            replaced_lines.append(line)

        replaced_text = '\n'.join(replaced_lines)
        self.yaml = self.load(replaced_text)

    def set_agent(self, agent_name):
        # Set pipeline agent to point to local agent
        self.yaml["pool"] = {
            "name": "Default",
            "demands": [f"agent.name -equals {agent_name}"]
        }

    def dump(self, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, self.yaml, stream, **kw)
        if inefficient:
            return stream.getvalue()
