from datetime import timedelta

import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator

from handlers.machine import check_instance_handler
from dags.handlers.command import application_init_handler
from handlers.command import system_init_handler
from handlers.command import wait_application_init_finish_handler
from handlers.command import wait_system_init_state_handler
from handlers.machine import check_network_ok
from handlers.machine import create_instance_handler
from handlers.machine import wait_instance_state_finish_handler

default_args = {
    'owner': 'zhengyansheng',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
}

dag = DAG(
    'delivery_machine',
    default_args=default_args,
    description='交付机器',
    schedule_interval=None,
)

"""
POST /api/v1/scheduler/<dag_name>
content-type: application/json
Authorization: JWT xxx
{

}
"""

t1 = PythonOperator(
    task_id='check_instance',
    provide_context=True,
    python_callable=check_instance_handler,
    dag=dag,
)

# t2 = PythonOperator(
#     task_id='create_instance',
#     provide_context=True,
#     python_callable=create_instance_handler,
#     dag=dag,
# )
#
# t3 = PythonOperator(
#     task_id='wait_instance_state_finish',
#     provide_context=True,
#     python_callable=wait_instance_state_finish_handler,
#     dag=dag,
# )
#
# t4 = PythonOperator(
#     task_id='check_network_ok',
#     provide_context=True,
#     python_callable=check_network_ok,
#     dag=dag,
# )
#
# t5 = PythonOperator(
#     task_id='system_init',
#     provide_context=True,
#     python_callable=system_init_handler,
#     dag=dag,
# )
#
# t6 = PythonOperator(
#     task_id='wait_system_init_state',
#     provide_context=True,
#     python_callable=wait_system_init_state_handler,
#     retries=5,
#     retry_delay=timedelta(seconds=30),
#     dag=dag,
# )
#
# t7 = PythonOperator(
#     task_id='application_init',
#     provide_context=True,
#     python_callable=application_init_handler,
#     dag=dag,
# )
#
# t8 = PythonOperator(
#     task_id='wait_application_init_finish',
#     provide_context=True,
#     python_callable=wait_application_init_finish_handler,
#     retries=5,
#     retry_delay=timedelta(seconds=60),
#     dag=dag,
# )
#
# t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7 >> t8
t1
