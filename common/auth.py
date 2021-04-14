from .http import Http
from config.config import DagConfig


def LightningAuth(username, password):
    url = f"http://{DagConfig.LIGHTNING_OPS_HOST}:{DagConfig.LIGHTNING_OPS_PORT}/api/v1/api-token-auth/"
    print(f"current post url: {url}")
    data = {"username": username, "password": password}
    response, ok = Http.Post(url, data)
    if not ok:
        return response, False
    return response['token'], True