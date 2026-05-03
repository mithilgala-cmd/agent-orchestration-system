import os
import base64
import logging
import docker

logger = logging.getLogger(__name__)


class DockerSandbox:
    def __init__(self, image: str = "python:3.11-slim"):
        self.image = image
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    def execute_code(self, code: str, timeout: int = 30) -> dict:
        """
        Execute Python code in an isolated Docker container.
        Code is base64-encoded to avoid shell quote-escaping issues on Windows.
        """
        try:
            encoded = base64.b64encode(code.encode("utf-8")).decode("ascii")
            command = (
                f'python -c "'
                f'import base64; exec(base64.b64decode(\\"{encoded}\\").decode())"'
            )
            output = self.client.containers.run(
                self.image,
                command=command,
                detach=False,
                stdout=True,
                stderr=True,
                remove=True,
                mem_limit="128m",
                network_disabled=True,
                timeout=timeout,
            )
            return {"status": "success", "output": output.decode("utf-8")}
        except docker.errors.ContainerError as e:
            return {"status": "error", "output": e.stderr.decode("utf-8")}
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return {"status": "error", "output": str(e)}


# Singleton
sandbox = DockerSandbox()
