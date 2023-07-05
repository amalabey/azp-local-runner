# azp-local-runner
Azure Pipelines Local Runner is a tool to validate, run and debug pipelines in your local machine. Developing Azure Pipelines is a time-consuming task, mainly because the troubleshooting is often done by lengthy trial and error cycles. In real-world scenarios, the time to test a pipeline change/fix could take significantly longer due to pipeline agents being busy performing other builds/deployments. Azure Pipelines does not support running pipelines in a developer machine outside of a Pipelines Agent. This tool solves some of those problems by allowing developers to run pipelines in their local developer machine (in a Docker container side-car). Furthermore, it allows setting breakpoints in the Yaml workflows, which provides a shell when the breakpoint is hit.  

![Pipeline Debugging Screen](/docs/pipeline-debugging.gif)  

## Key Features
 Below are some key features to make the pipeline development experience better.
- **Validate Yaml pipelines before pushing to the repository**
- **Running pipelines locally in a side-car container**
- **Adding breakpoints and gaining shell access when the breakpoint is hit**
- **Access file system contents at pipeline run time**
- **Viewing pipeline logs feed**

### LIMITATIONS
- Supports only workflows that can run on Linux agents  


## How does it work?
It runs an Azure Pipelines [self-hosted docker agent](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/docker?view=azure-devops) as a side-car. The tool creates a dedicated agent pool and registers the container agent in the pool. It then updates your Pipeline Yaml in a remote temporary branch to use the given agent instead. It also adds a Python one-liner reverse shell in-place of all breakpoints (`#breakpoint`) in your Yaml. It uses Azure Pipelines REST API to run the pipeline and starts a listener to receive a reverse shell from the local docker agent. When the breakpoint is reached, the workflow runs the reverse shell script and connects to the listener, allowing you to run any shell commands on the agent while the workflow is paused. 

# Getting Started
You can install the tool by running below:
```
pip3 install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple azplocal
```
You need below before you can start using the tool:
* You should be running docker and logged in so that you can pull container images from [Docker Hub](https://hub.docker.com/repository/docker/amalabey/azp-local-runner/general).
* [PAT](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows) to access your Azure DevOps instance. The PAT should have permission to create agent pools, register agents, update repository files and run workflows.
* Url to Azure DevOps organisation and the project name
* Id of the Pipeline in Azure Pipelines. You can take this from `definitionId` query parameter value in the Url when you access the pipeline in the browser.
* Path to your local repository where the Yaml pipeline lives 

## Validating Yaml Pipeline
The tool uses Azure Pipelines [Runs REST Api](https://learn.microsoft.com/en-us/rest/api/azure/devops/pipelines/runs/run-pipeline?view=azure-devops-rest-7.0) to validate the yaml. The below command will write the final validate Yaml to a file named "final_validated.yml".
```
azplocal validate -o https://dev.azure.com/<org-name> -p <project-name> -t <personal-access-token> -i <pipeline-id> -r <absolute-path-to-local-git-repository> -f <yaml-file-path-relative-to-repo>
```  
## Running/Debugging Pipeline
You can execute the below command to run the pipeline. Optionally, you can pass in the "-d/--debug" flag to start debugging. When debugging, you can add breakpoints to your main pipeline Yaml or sub-templates by adding `#breakpoint` comment in Yaml. Please ensure this comment is indented properly as it aligns with the pipeline steps/tasks.
```
azplocal run -o https://dev.azure.com/<org-name> -p <project-name> -t <personal-access-token> -i <pipeline-id> -r <absolute-path-to-local-git-repository> -f <yaml-file-path-relative-to-repo> [--debug] [--image <custom-agent-image-name>]
```
When debugging, you will see "Connected to agent..." appear on your Debug Console. This means your pipeline is now paused at the breakpoint, and you have a shell to the pipeline runtime to perform any troubleshooting. You can simply execute any shell command at this point to view its output. When you want to continue, send the `exit` command, and the pipeline will continue from that point onwards.
The Debug Shell also supports several special commands as listed below:
- `#upgrade`: Upgrades your reverse shell using Python's `pty` for a better experience
- `#serve`: Starts a web server on http://localhost:7073, allowing you to browse/access the agent file system

### Using Custom Agent Image
If your pipeline requires, additional/special software to be available on the agent, you can take the Dockerfile in this repository and customise it to include any additional software. Then you can build a Docker image using `docker build . --platform linux/amd64 -t <your-image-name>:latest`. When running the pipeline, you can pass `-a` parameter to specify your image name.]