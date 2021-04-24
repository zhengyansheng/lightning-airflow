from pprint import pprint
from config.config import DagConfig

from .http import Http


def query_instance_info_by_private_ip(private_ip, source_cmdb=True):
    """
    从 cmdb 接口查询 或者 从 lightning-ops 查询
    """
    if source_cmdb:
        url = f"http://{DagConfig.LIGHTNING_OPS_HOST}:{DagConfig.LIGHTNING_OPS_PORT}/api/v1/cmdb/instances/?private_ip={private_ip}"
        print(f"current get url: {url}")
        response, ok = Http.Get(url)
        if not ok:
            return f"Http get, err: {response}", False

        if response['code'] == -1:
            return f"response, err: {response['message']}", False

        return response['data']['results'][0], True
    else:
        return {}, True


def operation_instance(action, json_data):
    """
    调用 lightning-ops 执行常规操作
    start | stop | ...
    """
    uri = f"/api/v1/multi-cloud/instance/{action}"
    url = f"http://{DagConfig.LIGHTNING_GO_HOST}:{DagConfig.LIGHTNING_GO_PORT}{uri}"
    print(f"current url: {url}")
    response, ok = Http.Post(url, json_data)
    pprint(response)
    if not ok:
        return f"Http post err: {response}", False

    if response['code'] == -1:
        return f"response, err: {response['message']}", False

    return "", True


def multi_update_instance_to_cmdb(data_list):
    url = f"http://{DagConfig.LIGHTNING_OPS_HOST}:{DagConfig.LIGHTNING_OPS_PORT}/api/v1/cmdb/instances/multi_update/"
    print(f"current put url: {url}")
    response, ok = Http.Put(url, data_list)
    pprint(response)
    if not ok:
        return f"Http post, err: {response}", False

    if response['code'] == -1:
        return f"response, err: {response['message']}", False

    return "", True
