import json

from common.exceptions import AirflowHttpExcept


def parse_dag_run(func):
    def wrapper(*args, **kwargs):
        print(f" -> wrapper args: {args}, kwargs: {kwargs}.")

        # 1. 获取 dag_run 配置信息
        config = kwargs['dag_run'].conf
        print(f" -> wrapper config: {config}")

        # 2. 获取提交到数据
        data = config.get("data", None)
        print(f" -> wrapper data: {data}, type data: {type(data)}")
        if data and isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception as e:
                raise AirflowHttpExcept(f"Json loads, err: {e.args}")

        # creator = config.get("creator", None)
        # uuid = config.get("uuid", None)

        return func(*args, **data)

    return wrapper
