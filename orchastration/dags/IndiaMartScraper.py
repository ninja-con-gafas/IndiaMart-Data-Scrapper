from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

with DAG(dag_id='IndiaMartScraper', default_args=default_args, description='Scrapy spiders orchestration for IndiaMart categories',
         schedule_interval=None, start_date=datetime(2025, 5, 1), catchup=False, tags=['IndiaMart', 'Scraping']) as dag:
    run_indiamart_category = BashOperator(
        task_id='run_indiamart_category_spider',
        bash_command=(
            "cd /opt/airflow/Scraper && "
            "scrapy crawl IndiaMartCategory "
            "-a path=/data/targets.txt "
            "-o /data/sub_category_output.json"
        )
    )

    run_indiamart_sub_category = BashOperator(
        task_id='run_indiamart_subcategory_spider',
        bash_command=(
            "cd /opt/airflow/Scraper && "
            "scrapy crawl IndiaMartSubCategory "
            "-a path=/data/sub_category_output.json "
            "-o /data/sub_sub_category_output.json"
        )
    )

    run_indiamart_category >> run_indiamart_sub_category
