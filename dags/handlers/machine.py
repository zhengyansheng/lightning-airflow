from pprint import pprint

from common.auth import LightningAuth
from common.exceptions import AirflowHttpExcept
from common.exec_http import operation_instance
from common.exec_http import query_instance_info_by_private_ip
from common.exec_http import multi_update_instance_to_cmdb
from common.http import Http
from config.config import DagConfig


def check_instance_handler(*args, **kwargs):
    # 解析参数

    return


def create_instance_handler(*args, **kwargs):
    # 解析参数
    data = kwargs['dag_run'].conf
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

    # {'code': 0, 'data': {'instance_id': 'i-2ze3vpnhvpod3xlzpkpr'}, 'message': 'Ok', 'request_id': ''}
    instance_info = response['data']
    # push share k/v
    _data = {
        "instance_id": instance_info['instance_id'],
        "account": data['account'],
    }
    kwargs['ti'].xcom_push(key='push_job_id', value=_data)
    return response


def wait_instance_state_finish_handler(*args, **kwargs):
    # 解析参数
    data = kwargs['dag_run'].conf

    # pull share k/v
    job = kwargs["ti"].xcom_pull(task_ids='create_instance', key='push_job_id')
    print(f"->instance_id: {job['instance_id']}")

    # 组合URL
    uri = f"/api/v1/multi-cloud/instance/{job['instance_id']}?account={data['account']}&region_id={data['region_id']}"
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
    job = kwargs["ti"].xcom_pull(task_ids='create_instance', key='push_job_id')
    print(f"->instance_id: {job['instance_id']}")
    print(f"->account: {job['account']}")

    # 组合URL
    uri = f"/api/v1/multi-cloud/instance/{job['instance_id']}?account={data['account']}&region_id={data['region_id']}"
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
    _data = response['data']
    _data['account'] = job['account']
    response, ok = Http.Post(url, _data)
    if not ok:
        raise AirflowHttpExcept(f"Http post, err: {response}")

    if response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {response['message']}")

    pprint(response)


def join_tree_handler(*args, **kwargs):
    """
    加入归属
    """
    # 解析参数
    data = kwargs['dag_run'].conf
    # 查询cmdb id

    # 检查
    data = kwargs['dag_run'].conf
    if 'app_key' not in data:
        raise AirflowHttpExcept("app_key is required.")

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
    tree_param_data = {"app_key": data['app_key'], "cmdbs": [cmdbPk]}  # TODO
    headers = {
        "content-type": "application/json",
        "Authorization": "JWT {}".format(jwt_token)
    }
    pprint(headers)
    pprint(tree_param_data)
    response, ok = Http.Post(url, tree_param_data, headers=headers)
    pprint(ok)
    pprint(response)
    if not ok:
        raise AirflowHttpExcept(f"Http post, err: {response}")

    if response['code'] == -1:
        raise AirflowHttpExcept(f"response, err: {response['message']}")

    pprint(response)


# 通用实例
# start, stop, restart, destroy
def common_instance_handler(action, *args, **kwargs):
    # 1. 解析参数
    data = kwargs['dag_run'].conf
    print(f"data: {data}")

    # 2. 查询详情
    instance_info, ok = query_instance_info_by_private_ip(private_ip=data['private_ip'], source_cmdb=True)
    if not ok:
        raise AirflowHttpExcept(instance_info)

    # 3. 执行动作
    json_data = {
        "account": instance_info['account'],
        "region_id": instance_info['region_id'],
        "instance_id": instance_info['instance_id'],
    }
    result, ok = operation_instance(action, json_data)
    if not ok:
        raise AirflowHttpExcept(result)

    return


def sync_instance_info_handler(*args, **kwargs):
    # 1, 解析参数
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")
    data = kwargs['dag_run'].conf
    print(f"data: {data}")

    # 2. 查询详情
    instance_info, ok = query_instance_info_by_private_ip(private_ip=data['private_ip'], source_cmdb=True)
    if not ok:
        raise AirflowHttpExcept(instance_info)

    # 3. update instance state
    state_m = {
        "is_deleted": kwargs.get('is_deleted', False),
    }
    update_instance_state(instance_info['account'], instance_info['region_id'], instance_info['instance_id'], state_m)


### 通用函数 ###


def update_instance_state(account, region_id, instance_id, state_m={}):
    """
    通用修改实例状态
    """
    # 1. 查询实例详情
    uri = f"/api/v1/multi-cloud/instance/{instance_id}?account={account}&region_id={region_id}"
    url = f"http://{DagConfig.LIGHTNING_GO_HOST}:{DagConfig.LIGHTNING_GO_PORT}{uri}"
    print(f"current get url: {url}")
    response, ok = Http.Get(url)
    pprint(response)
    if not ok:
        raise AirflowHttpExcept(f"Http get, err: {response}")

    # 2. 批量修改实例信息
    tmp_data = {
        "private_ip": response['data']['private_ip'],
    }
    tmp_data.update(state_m)
    data_list = [tmp_data]
    result, ok = multi_update_instance_to_cmdb(data_list)
    if not ok:
        raise AirflowHttpExcept(result)

    return
