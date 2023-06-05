# azp-local-runner
Attempt to improve Azure Pipelines developer experience by allowing to test the yaml on a self-hosted agent in a container


## Build Agent

```
docker run -e AZP_URL=<Azure DevOps instance> -e AZP_TOKEN=<PAT token> -e AZP_AGENT_NAME=<AGENT NAME> -n azp-agent azp-local-agent:latest
```