import docker
from app.azure_pipelines_client import AzurePipelinesClient

AGENT_VOLUME_NAME = "azp-work-volume"
AGENT_POOL_NAME = "azplocal"


class LocalAgent():
    def __init__(self, org_url, project_name, personal_access_token, name,
                 image_name):
        self.org_url = org_url
        self.project_name = project_name
        self.personal_access_token = personal_access_token
        self.image_name = image_name
        self.container_name = f"azp-{name}"
        self.agent_name = f"azp-{name}"
        self.agent_pool_name = AGENT_POOL_NAME

    def get_agent_name(self):
        return self.agent_name

    def get_agent_pool_name(self):
        return self.agent_pool_name

    def _container_exists(self, client, container_name):
        containers = client.containers.list(all=True)
        for container in containers:
            if container.name == container_name:
                return True
        return False

    def start(self):
        azure_pipelines_client = AzurePipelinesClient(self.org_url,
                                                      self.project_name,
                                                      self.personal_access_token)
        azure_pipelines_client.register_agent_pool(self.agent_pool_name)

        client = docker.from_env()
        agent_params = {
            "AZP_URL": self.org_url,
            "AZP_TOKEN": self.personal_access_token,
            "AZP_AGENT_NAME": self.agent_name,
            "AZP_POOL": self.agent_pool_name
        }

        existing_volumes = client.volumes.list(filters={
            'name': self.image_name
            })
        if existing_volumes:
            volume = existing_volumes[0]
        else:
            volume = client.volumes.create(name=AGENT_VOLUME_NAME)

        if not self._container_exists(client, self.container_name):
            client.containers.run(self.image_name,
                                  volumes={
                                        volume.name: {
                                                "bind": "/azp/_work",
                                                "mode": "rw"
                                        }
                                    },
                                  detach=True,
                                  name=self.container_name,
                                  ports= {7073: 7073},
                                  platform="linux/amd64",
                                  environment=agent_params)
        else:
            container = client.containers.get(self.container_name)
            container.start()
