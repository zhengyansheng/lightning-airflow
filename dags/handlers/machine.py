from common.http import Http
from config.config import Config
from dags.parse import parse_dag_run


def check_instance_handler(*args, **kwargs):
    print(f"args-> {args}")
    print(f"kwargs-> {kwargs}")


@parse_dag_run
def create_instance_handler(*args, **kwargs):
    print(f"args-> {args}")
    print(f"kwargs-> {kwargs}")
    uri = "/api/v1/multi-cloud/instance/create"
    url = f"http://{Config.LIGHTNING_GO_HOST}:{Config.LIGHTNING_GO_PORT}{uri}"
    print(f"current url: {url}")


def wait_instance_state_finish_handler(*args, **kwargs):
    print(f"args-> {args}")
    print(f"kwargs-> {kwargs}")


def check_network_ok(*args, **kwargs):
    """探测网络是否可达 ping / telnet """
    print(f"args-> {args}")
    print(f"kwargs-> {kwargs}")
