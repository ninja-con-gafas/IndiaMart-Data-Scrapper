import json
import os
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from typing import List

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

    run_indiamart_category = BashOperator(
        task_id='run_indiamart_category_spider',
        bash_command=(
            "cd /opt/airflow/Scraper && "
            "scrapy crawl IndiaMartCategory "
            "-a path=/data/targets.txt "
            "-o /data/sub_category_output.json"
        ),
        queue="default"
    )

    run_indiamart_sub_category = BashOperator(
        task_id='run_indiamart_subcategory_spider',
        bash_command=(
            "cd /opt/airflow/Scraper && "
            "scrapy crawl IndiaMartSubCategory "
            "-a path=/data/sub_category_output.json "
            "-o /data/sub_sub_category_output.json"
        ),
        queue="default"
    )

    @task(task_id='split_sub_sub_category_output_file')
    def split_file(path: str ="/data/sub_sub_category_output.json", parts: int =4) -> List[str]:
        with open(path) as in_file:
            data = json.load(in_file)

        os.makedirs("/data/parts", exist_ok=True)
        os.makedirs("/data/products", exist_ok=True)

        chunk_size = len(data) // parts + (len(data) % parts > 0)
        output_paths: List[str] = []

        for part in range(parts):
            chunk = data[part * chunk_size: (part + 1) * chunk_size]
            chunk_path = f"/data/parts/sub_sub_category_output_part_{part}.json"
            with open(chunk_path, "w") as out_file:
                json.dump(chunk, out_file)
            output_paths.append(chunk_path)

        return output_paths

    split_sub_sub_category = split_file()

    run_indiamart_product = BashOperator.partial(
        task_id='run_indiamart_product_spider',
        bash_command=(
            "cd /opt/airflow/Scraper && "
            "scrapy crawl IndiaMartProduct "
            "-a path={{ params.input_file }} "
            "-o /data/products/products_part_{{ params.input_file.split('_')[-1].split('.')[0] }}.json"
        ),
        queue='heavy'
    ).expand(params=split_sub_sub_category.map(lambda file: {'input_file': file}))

    run_indiamart_category >> run_indiamart_sub_category >> split_sub_sub_category >> run_indiamart_product
