from datetime import timedelta

import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator

from dags.handlers.machine import check_instance_handler
from dags.handlers.machine import reboot_instance_handler
from dags.handlers.machine import sync_instance_info_handler

default_args = {
    'owner': 'zhengyansheng',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
}

# Dag 实例化
dag = DAG(
    'reboot_instance',
    default_args=default_args,
    description='重启实例',
    # 外部触发
    schedule_interval=None,
)

"""Example
POST /api/v1/scheduler/<dag_name>
content-type: application/json
Authorization: JWT xxx
{
}
"""

# 检查实例
t1 = PythonOperator(
    task_id='check_instance',
    provide_context=True,
    python_callable=check_instance_handler,
    dag=dag,
)

# 启动主机
t2 = PythonOperator(
    task_id='reboot_instance',
    provide_context=True,
    python_callable=reboot_instance_handler,
    op_kwargs={"action": "reboot"},
    dag=dag,
)

# 同步信息
t3 = PythonOperator(
    task_id='sync_instance_info',
    provide_context=True,
    python_callable=sync_instance_info_handler,
    dag=dag,
)


t1 >> t2 >> t3
