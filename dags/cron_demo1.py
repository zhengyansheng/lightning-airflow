from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator


default_args = {
    'owner': 'zhengyansheng',
    'start_date': days_ago(2)
}

dag = DAG(
    dag_id='cron_demo1',
    default_args=default_args,
    schedule_interval='*/50 * * * *')


t1 = BashOperator(
           task_id="echo_hello_world",
           bash_command='echo Hello World!',
           dag=dag)

t1
