#!/usr/bin/env python3
import argparse
import base64
import docker
import requests
import json
import logging
import http.client
from git import Repo
import socket
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
import socket, sys, time
import signal

AGENT_IMAGE_NAME = "azp-local-agent:latest"
BREAKPOINT_COMMENT = "#breakpoint"
BREAKPOINT_SCRIPT = "- script: export RHOST=\"host.docker.internal\";export RPORT=4242;python3 -c \'import socket,os,pty;s=socket.socket();s.connect((os.getenv(\"RHOST\"),int(os.getenv(\"RPORT\"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn(\"/bin/sh\")\'"
AGENT_VOLUME_NAME = "azp-work-volume"

httpclient_logger = logging.getLogger("http.client")


class StringExportableYaml(YAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


def listen_rvshell(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen(1)
    print("Waiting for break point hit... ")
    conn, addr = sock.accept()
    print('Connected to agent: ', addr)
    # Upgrade connection using pty
    # upgrade_cmd = "python3 -c \'import pty; pty.spawn(\"/bin/sh\")\'\n\n"
    # conn.send(upgrade_cmd.encode('utf-8'))
    while True:
        # Receive data from the target and get user input
        data = conn.recv(1024)
        if not data:
            print("Connection closed")
            sock.close()
            break

        ans = data.decode()
        sys.stdout.write(ans)
        command = input()

        # Send command
        command += "\n"
        conn.send(command.encode())
        time.sleep(1)

        # Remove the output of the "input()" function
        sys.stdout.write("\033[A" + ans.split("\n")[-1])


def insert_breakpoints(yaml_text):
    lines = yaml_text.split('\n')
    replaced_lines = []

    for line in lines:
        if line.strip() == BREAKPOINT_COMMENT:
            indent = len(line) - len(line.lstrip())
            line = ' ' * indent + BREAKPOINT_SCRIPT
        replaced_lines.append(line)

    replaced_text = '\n'.join(replaced_lines)
    return replaced_text


def get_updated_pipeline_yaml(repo_path, file_path, agent_name):
    yaml = StringExportableYaml()
    with open(f"{repo_path}/{file_path}", 'r') as file:
        yaml_file_contents = file.read()
        yaml_file_contents = insert_breakpoints(yaml_file_contents)
        yaml_data = yaml.load(yaml_file_contents)
        # Set pipeline agent to point to local agent
        yaml_data["pool"] = {
            "name": "Default",
            "demands": [f"agent.name -equals {agent_name}"]
        }
        # Add reverse shells to breakpoint comments
        yaml_text = yaml.dump(yaml_data)
        return yaml_text


def container_exists(client, container_name):
    containers = client.containers.list(all=True)
    for container in containers:
        if container.name == container_name:
            return True
    return False


def start_local_agent(org_url, personal_access_token, container_name, agent_name):
    client = docker.from_env()
    agent_params = {
        "AZP_URL": org_url,
        "AZP_TOKEN": personal_access_token,
        "AZP_AGENT_NAME": agent_name
    }

    existing_volumes = client.volumes.list(filters={'name': AGENT_VOLUME_NAME})
    if existing_volumes:
        volume = existing_volumes[0]
    else:
        volume = client.volumes.create(name=AGENT_VOLUME_NAME)

    if not container_exists(client, container_name):
        client.containers.run(AGENT_IMAGE_NAME,
                              volumes={
                                  volume.name: {
                                        "bind": "/azp/_work",
                                        "mode": "rw"
                                  }
                              },
                              detach=True,
                              name=container_name,
                              environment=agent_params)
    else:
        container = client.containers.get(container_name)
        container.start()


def recreate_temp_branch(org_url, project_name, personal_access_token, repo_path):
    git_username = get_git_username(repo_path)
    git_username_hash = generate_unique_int(git_username)
    temp_branch_name = f"tmp-{pipeline_id}-{git_username_hash}"

    # Delete the temp branch if it already exists
    existing_remote_ref = get_remote_branch(org_url, project_name, personal_access_token, temp_branch_name)
    if len(existing_remote_ref["value"]) > 0:
        delete_temp_branch(org_url, project_name, personal_access_token, temp_branch_name, existing_remote_ref["value"][0]["objectId"])

    # Get the remote tracking branch for the currently active branch
    active_branch_name = get_active_branch_name(repo_path)
    remote_tracking_ref = get_remote_branch(org_url, project_name, personal_access_token, active_branch_name)
    if len(remote_tracking_ref["value"]) == 0:
        raise Exception("Unable to find the remote tracking branch for the active branch. Please publish the branch")
    object_id = remote_tracking_ref["value"][0]["objectId"]

    # Create the new temp branch
    temp_branch_ref = create_temp_branch(org_url, project_name, personal_access_token, temp_branch_name, object_id)
    return (temp_branch_ref["value"][0]["name"], temp_branch_ref["value"][0]["newObjectId"])


def get_active_branch_name(repo_path):
    try:
        repo = Repo(repo_path)
        return repo.active_branch.name
    except Exception as e:
        print("Error: Unable to get remote branch name.", str(e))
        return None


def delete_temp_branch(org_url, project_name, personal_access_token, branch_name, commit_id):
    api_url = f"{org_url}/{project_name}/_apis/git/repositories/{project_name}/refs?api-version=6.0"
    payload = json.dumps([
        {
            "name": f"refs/heads/{branch_name}",
            "oldObjectId": commit_id,
            "newObjectId": "0000000000000000000000000000000000000000"
        }
    ])
    response = send_api_request(api_url, personal_access_token, 'POST', payload)
    return response


def create_temp_branch(org_url, project_name, personal_access_token, branch_name, commit_id):
    api_url = f"{org_url}/{project_name}/_apis/git/repositories/{project_name}/refs?api-version=6.0"
    payload = json.dumps([
        {
            "name": f"refs/heads/{branch_name}",
            "oldObjectId": "0000000000000000000000000000000000000000",
            "newObjectId": commit_id
        }
    ])
    response = send_api_request(api_url, personal_access_token, 'POST', payload)
    return response


def update_remote_file(org_url, project_name, personal_access_token, ref_name, object_id, file_path, file_content):
    api_url = f"{org_url}/{project_name}/_apis/git/repositories/eShopOnWeb/pushes?api-version=7.0"
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
    response = send_api_request(api_url, personal_access_token, 'POST', payload)
    return response


def get_remote_branch(org_url, project_name, personal_access_token, branch_name):
    ref_api_url = f"{org_url}/{project_name}/_apis/git/repositories/{project_name}/refs?filterContains={branch_name}&api-version=6.0"
    response = send_api_request(ref_api_url, personal_access_token, 'GET')
    return response


def generate_unique_int(text):
    number = sum(ord(c) for c in text)
    return number


def get_git_username(repo_path):
    try:
        repo = Repo(repo_path)
        git_username = repo.config_reader().get_value('user', 'name')
        return git_username
    except Exception as e:
        print("Error: Unable to get git username.", str(e))
        return None


def httpclient_logging_patch(level=logging.DEBUG):
    """Enable HTTPConnection debug logging to the logging framework"""

    def httpclient_log(*args):
        httpclient_logger.log(level, " ".join(args))

    # mask the print() built-in in the http.client module to use
    # logging instead
    http.client.print = httpclient_log
    # enable debugging
    http.client.HTTPConnection.debuglevel = 1


def send_api_request(url, personal_access_token, method="GET", data=None):
    header_value = f":{personal_access_token}"
    header_bytes = header_value.encode('utf-8')
    basic_auth_header_bytes = base64.b64encode(header_bytes)
    basic_auth_header = basic_auth_header_bytes.decode('utf-8')
    headers = {
        "Authorization": f"Basic {basic_auth_header}",
        "Content-Type": "application/json"
    }

    response = requests.request(method, url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()


def run_pipeline(org_url, project_name, pipeline_id, personal_access_token, ref_name):
    run_api_url = f"{org_url}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
    payload = json.dumps({
        "resources": {
            "repositories": {
                "self": {
                    "refName": ref_name
                }
            }
        }
    })
    response = send_api_request(run_api_url, personal_access_token, 'POST', payload)
    return response


def validate_pipeline(org_url, project_name, pipeline_id, personal_access_token, repo_path, file_path):
    run_api_url = f"{org_url}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
    file_content = read_yaml_to_string(f"{repo_path}/{file_path}")
    payload = json.dumps({
        "previewRun": True,
        "yamlOverride": file_content
    })
    response = send_api_request(run_api_url, personal_access_token, 'POST', payload)
    write_yaml_to_file("final.yml", response["finalYaml"])
    return response


def write_yaml_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)


def read_yaml_to_string(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content


# Define a signal handler for Ctrl+C
def signal_handler(signal, frame):
    print("Ctrl+C received. Performing shutdown actions...")
    # Perform shutdown actions
    # if sock is not None:
    #     # sock.shutdown(socket.SHUT_RDWR)
    #     sock.close()
    # Exit the program
    sys.exit(0)


# Set the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Create the argument parser
parser = argparse.ArgumentParser(description='Running and debugging Azure Pipelines on a local docker container')

# Add arguments
parser.add_argument('-o', '--org', type=str, help='Url to Azure DevOps organisation')
parser.add_argument('-p', '--project', type=str, help='Azure DevOps project name')
parser.add_argument('-t', '--token', type=str, help='Personal Access Token to access Azure DevOps')
parser.add_argument('-f', '--file', type=str, help='Azure Pipeline Yaml file')
parser.add_argument('-r', '--repo_path', type=str, help='Repository path')
parser.add_argument('-i', '--id', type=str, help='Pipeline Id from Azure Pipelines (can be found in the url)')
parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
parser.add_argument("--validate", action="store_true", help="Enable verbose logging")

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the parsed arguments
org_url = args.org
token = args.token
project_name = args.project
file_path = args.file
pipeline_id = args.id
repo_path = args.repo_path

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
    httpclient_logging_patch()

if args.validate:
    result = validate_pipeline(org_url, project_name, pipeline_id, token, repo_path, file_path)
    print(result)
else:
    hostname = socket.gethostname()
    identifier = hostname.replace(" ", "").lower()
    agent_name = f"agent-{identifier}"
    start_local_agent(org_url, token, agent_name, agent_name)
    ref_name, object_id = recreate_temp_branch(org_url, project_name, token, repo_path)
    yaml_content = get_updated_pipeline_yaml(repo_path, file_path, agent_name)
    update_remote_file(org_url, project_name, token, ref_name, object_id, file_path, yaml_content)
    result = run_pipeline(org_url, project_name, pipeline_id, token, ref_name)
    print(result)
    while True:
        listen_rvshell("0.0.0.0", 4242)
