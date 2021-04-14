from pprint import pprint

from common.exceptions import AirflowHttpExcept
from common.http import Http
from common.auth import LightningAuth
from config.config import DagConfig


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
    url = f"http://{DagConfig.LIGHTNING_GO_HOST}:{DagConfig.LIGHTNING_GO_PORT}{uri}"
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
    # 解析参数
    data = kwargs['dag_run'].conf

    # pull share k/v
    instance_id = kwargs["ti"].xcom_pull(task_ids='create_instance', key='push_job_id')
    print(f"->instance_id: {instance_id}")

    # 组合URL
    uri = f"/api/v1/multi-cloud/instance/{instance_id}?account={data['account']}&region_id={data['region_id']}"
    url = f"http://{DagConfig.LIGHTNING_GO_HOST}:{DagConfig.LIGHTNING_GO_PORT}{uri}"
    print(f"current url: {url}")

    # 发起请求
    response, ok = Http.Get(url)
    if not ok:
        raise AirflowHttpExcept(f"Http get, err: {response}")
    pprint(response)

    if response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {response['message']}")

    if response['data']['state'] == "stopped":
        raise AirflowHttpExcept(f"instance state err, current state is {response['data']['state']}")


    # push share k/v
    kwargs["ti"].xcom_push(key='push_job_id', value=response['data']['private_ip'])


def check_network_ok_handler(*args, **kwargs):
    """探测网络是否可达 ping / telnet """
    print(f"args-> {args}")
    print(f"kwargs-> {kwargs}")


def push_metadata_cmdb_handler(*args, **kwargs):
    """
    Push instance metadata to cmdb
    """
    # 解析参数
    data = kwargs['dag_run'].conf

    # pull share k/v
    instance_id = kwargs["ti"].xcom_pull(task_ids='create_instance', key='push_job_id')
    print(f"->instance_id: {instance_id}")

    # 组合URL
    uri = f"/api/v1/multi-cloud/instance/{instance_id}?account={data['account']}&region_id={data['region_id']}"
    url = f"http://{DagConfig.LIGHTNING_GO_HOST}:{DagConfig.LIGHTNING_GO_PORT}{uri}"
    print(f"current get url: {url}")

    # 发起请求 GET 查询
    response, ok = Http.Get(url)
    if not ok:
        raise AirflowHttpExcept(f"Http post, err: {response}")
    pprint(response)

    # 组合URL
    url = f"http://{DagConfig.LIGHTNING_OPS_HOST}:{DagConfig.LIGHTNING_OPS_PORT}/api/v1/cmdb/instances/"
    print(f"current post url: {url}")

    # 发起请求 POST 提交
    response, ok = Http.Post(url, response['data'])
    if not ok:
        raise AirflowHttpExcept(f"Http post, err: {response}")

    if response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {response['message']}")

    pprint(response)


def join_tree_handler(*args, **kwargs):
    """
    加入归属
    """
    # 查询cmdb id
    # pull share k/v
    private_ip = kwargs["ti"].xcom_pull(task_ids='wait_instance_state_finish', key='push_job_id')
    print(f"->private_ip: {private_ip}")
    # http://ops.aiops724.com/api/v1/cmdb/instances/?page=1&page_size=8&search=172.17.118.29

    url = f"http://{DagConfig.LIGHTNING_OPS_HOST}:{DagConfig.LIGHTNING_OPS_PORT}/api/v1/cmdb/instances/?search={private_ip}"
    print(f"current post url: {url}")
    _response, ok = Http.Get(url)
    if not ok:
        raise AirflowHttpExcept(f"Http get, err: {_response}")

    if _response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {_response['message']}")

    cmdbPk = _response['data']['results'][0]['id']

    # 提交并加入到tree
    url = f"http://{DagConfig.LIGHTNING_OPS_HOST}:{DagConfig.LIGHTNING_OPS_PORT}/api/v1/service_tree/server/"
    print(f"current post url: {url}")

    # 获取JWT
    jwt_token, ok = LightningAuth(DagConfig.LIGHTNING_OPS_LOGIN_USERNAME, DagConfig.LIGHTNING_OPS_LOGIN_PASSWORD)
    if not ok:
        raise AirflowHttpExcept(f"get jwt , err: {jwt_token}")

    # 发起请求 POST 提交
    tree_param_data = {"node": 31, "cmdbs": [cmdbPk]} # TODO
    headers = {
        "content-type": "application/json",
        "Authorization": "JWT {}".format(jwt_token)
    }
    response, ok = Http.Post(url, tree_param_data, headers=headers)
    if not ok:
        raise AirflowHttpExcept(f"Http post, err: {response}")

    if response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {response['message']}")

    pprint(response)
