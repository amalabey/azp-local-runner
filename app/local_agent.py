import docker

DEFAULT_AGENT_IMAGE_NAME = "amalabey/azp-local-runner"
AGENT_VOLUME_NAME = "azp-work-volume"


class LocalAgent():
    def __init__(self, org_url, personal_access_token, name,
                 image_name=DEFAULT_AGENT_IMAGE_NAME):
        self.org_url = org_url
        self.personal_access_token = personal_access_token
        self.image_name = image_name
        self.container_name = f"azp-{name}"
        self.agent_name = f"azp-{name}"

    def get_agent_name(self):
        return self.agent_name

    def _container_exists(self, client, container_name):
        containers = client.containers.list(all=True)
        for container in containers:
            if container.name == container_name:
                return True
        return False

    def start(self):
        client = docker.from_env()
        agent_params = {
            "AZP_URL": self.org_url,
            "AZP_TOKEN": self.personal_access_token,
            "AZP_AGENT_NAME": self.agent_name
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
                                  environment=agent_params)
        else:
            container = client.containers.get(self.container_name)
            container.start()
