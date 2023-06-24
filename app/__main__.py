import argparse
from app.application import run_pipeline
from app.application import validate_pipeline

# Create the argument parser
parser = argparse.ArgumentParser(description='Running and debugging Azure Pipelines on a local docker container')

# Add arguments
parser.add_argument('-o', '--org', type=str, help='Url to Azure DevOps organisation')
parser.add_argument('-p', '--project', type=str, help='Azure DevOps project name')
parser.add_argument('-t', '--token', type=str, help='Personal Access Token to access Azure DevOps')
parser.add_argument('-f', '--file', type=str, help='Azure Pipeline Yaml file')
parser.add_argument('-r', '--repo_path', type=str, help='Repository path')
parser.add_argument('-i', '--id', type=str, help='Pipeline Id from Azure Pipelines (can be found in the url)')
parser.add_argument('-a', '--image', type=str, help='Agent image name to be used for local agent')
parser.add_argument("--validate", action="store_true", help="Enable verbose logging")
parser.add_argument("--debug", action="store_true", help="Enable verbose logging")

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the parsed arguments
org_url = args.org
token = args.token
project_name = args.project
file_path = args.file
pipeline_id = args.id
repo_path = args.repo_path
debug_flag = args.debug
agent_image_name = args.image

if args.validate:
    validate_pipeline(org_url, project_name, pipeline_id, token, repo_path,
                      file_path)
else:
    run_pipeline(org_url, project_name, pipeline_id, token, repo_path,
                 file_path, debug_flag, agent_image_name)
