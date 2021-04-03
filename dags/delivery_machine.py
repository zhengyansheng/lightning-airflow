from datetime import timedelta

import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator

from dags.handlers.command import application_init_handler
from dags.handlers.command import system_init_handler
from dags.handlers.command import wait_application_init_finish_handler
from dags.handlers.command import wait_system_init_state_handler
from dags.handlers.machine import check_instance_handler
from dags.handlers.machine import check_network_ok
from dags.handlers.machine import create_instance_handler
from dags.handlers.machine import wait_instance_state_finish_handler

default_args = {
    'owner': 'zhengyansheng',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
}

# Dag 实例化
dag = DAG(
    'delivery_machine',
    default_args=default_args,
    description='交付机器',
    # 外部触发
    schedule_interval=None,
)

"""Example
POST /api/v1/scheduler/<dag_name>
content-type: application/json
Authorization: JWT xxx
{
    "data": {
            "": "",
        }
}
"""

# 检查实例
t1 = PythonOperator(
    task_id='check_instance',
    provide_context=True,
    python_callable=check_instance_handler,
    dag=dag,
)

# 创建主机
t2 = PythonOperator(
    task_id='create_instance',
    provide_context=True,
    python_callable=create_instance_handler,
    xcom_push=True,
    dag=dag,
)

# 等待主机状态完成
t3 = PythonOperator(
    task_id='wait_instance_state_finish',
    provide_context=True,
    python_callable=wait_instance_state_finish_handler,
    retries=5,
    retry_delay=timedelta(seconds=30),
    dag=dag,
)

# 检查网络正常
t4 = PythonOperator(
    task_id='check_network_ok',
    provide_context=True,
    python_callable=check_network_ok,
    dag=dag,
)

# 系统初始化
t5 = PythonOperator(
    task_id='system_init',
    provide_context=True,
    python_callable=system_init_handler,
    dag=dag,
)

# 等待系统初始化状态完成
t6 = PythonOperator(
    task_id='wait_system_init_state',
    provide_context=True,
    python_callable=wait_system_init_state_handler,
    retries=5,
    retry_delay=timedelta(seconds=30),
    dag=dag,
)

# 应用初始化
t7 = PythonOperator(
    task_id='application_init',
    provide_context=True,
    python_callable=application_init_handler,
    dag=dag,
)

# 等待应用初始化状态完成
t8 = PythonOperator(
    task_id='wait_application_init_finish',
    provide_context=True,
    python_callable=wait_application_init_finish_handler,
    retries=5,
    retry_delay=timedelta(seconds=60),
    dag=dag,
)

t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7 >> t8
