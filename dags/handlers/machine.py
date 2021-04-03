from pprint import pprint

from common.exceptions import AirflowHttpExcept
from common.http import Http
from config.config import Config


def check_instance_handler(*args, **kwargs):
    print(f"args-> {args}")
    print(f"kwargs-> {kwargs}")


def create_instance_handler(*args, **kwargs):
    # 解析参数
    data = kwargs['dag_run'].conf
    ti = kwargs['ti']
    pprint(data)

    # 组合URL
    uri = "/api/v1/multi-cloud/instance/create"
    url = f"http://{Config.LIGHTNING_GO_HOST}:{Config.LIGHTNING_GO_PORT}{uri}"
    print(f"current url: {url}")

    # 发起请求
    response, ok = Http.Post(url, data)
    if not ok:
        raise AirflowHttpExcept(f"Http post, err: {response}")
    pprint(response)

    if response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {response['message']}")

    # {'code': 0, 'data': 'i-2ze3vpnhvpod3xlzpkpr', 'message': 'Ok', 'request_id': ''}
    instance_id = response['data']
    # push share k/v
    ti.xcom_push(key='push_job_id', value=instance_id)
    return response


def wait_instance_state_finish_handler(*args, **kwargs):
    # print(f"args-> {args}")
    # print(f"kwargs-> {kwargs}")

    # 解析参数
    data = kwargs['dag_run'].conf

    # pull share k/v
    instance_id = kwargs["ti"].xcom_pull(task_ids='create_instance', key='push_job_id')
    print(f"->instance_id: {instance_id}")

    # 组合URL
    uri = f"/api/v1/multi-cloud/instance/{instance_id}?account={data['account']}&region_id={data['region_id']}"
    url = f"http://{Config.LIGHTNING_GO_HOST}:{Config.LIGHTNING_GO_PORT}{uri}"
    print(f"current url: {url}")

    # 发起请求
    response, ok = Http.Get(url)
    if not ok:
        raise AirflowHttpExcept(f"Http post, err: {response}")
    pprint(response)

    if response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {response['message']}")

    if response['state'] == "stopped":
        raise AirflowHttpExcept(f"instance state err, current state is {response['state']}")


def check_network_ok(*args, **kwargs):
    """探测网络是否可达 ping / telnet """
    print(f"args-> {args}")
    print(f"kwargs-> {kwargs}")
