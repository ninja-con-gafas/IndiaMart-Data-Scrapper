from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from process.utilities import partition_json_by_key

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

with DAG(dag_id='IndiaMartScraper', 
         default_args=default_args, 
         description='Scrapy spiders orchestration for IndiaMart products',
         schedule_interval=None, 
         start_date=datetime(2025, 5, 1), 
         catchup=False, 
         tags=['IndiaMart', 'Scraping']) as dag:

    scrape_indiamart_category = BashOperator(
        task_id='scrape_indiamart_category',
        bash_command=(
            "cd /opt/airflow/scraper && "
            "scrapy crawl IndiaMartCategory "
            "-a path=/data/targets.txt "
            "-o /data/sub_category_output.json"
        )
    )

    scrape_indiamart_sub_category = BashOperator(
        task_id='scrape_indiamart_subcategory',
        bash_command=(
            "cd /opt/airflow/scraper && "
            "scrapy crawl IndiaMartSubCategory "
            "-a path=/data/sub_category_output.json "
            "-o /data/sub_sub_category_output.json"
        )
    )

    partition_sub_sub_category = PythonOperator(
        task_id="partition_sub_sub_category_files",
        python_callable=partition_json_by_key,
        op_kwargs={
            "input_file_path": "/data/sub_sub_category_output.json",
            "output_directory": "/tmp/IndiaMart/data/partitioned",
            "key": "sub_category"
        }
    )

    scrape_indiamart_product_listing = BashOperator.partial(
        task_id='scrape_indiamart_product_listing',
        bash_command=(
            "cd /opt/airflow/scraper && "
            "input_file={{ params.input_file }} && "
            "stem=$(basename ${input_file} .json) && "
            "scrapy crawl IndiaMartProductListing "
            "-a path=${input_file} "
            "-o /data/products/${stem}.json "
        )
    ).expand(params=partition_sub_sub_category.output.map(lambda file: {"input_file": file}))

    scrape_indiamart_category >> scrape_indiamart_sub_category >> partition_sub_sub_category >> scrape_indiamart_product_listing
