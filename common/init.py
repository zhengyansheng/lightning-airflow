import json

from common.exceptions import AirflowHttpExcept


def before_request(kwargs):
    ret = []

    # 1. 获取 dag_run 配置信息
    config = kwargs['dag_run'].conf
    print("config: {}".format(config))

    # 2. 获取提交到数据
    data = config.get("data", None)
    try:
        data = json.loads(data)
    except Exception as e:
        raise AirflowHttpExcept(f"Post data json loads error, err: {e.args}")

    creator = config.get("creator", None)
    uuid = config.get("uuid", None)

    return ret
