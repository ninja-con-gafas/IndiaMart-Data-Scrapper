# Slooze Data Engineering Challenge

This project implements an end-to-end data pipeline for extracting, processing, and storing product listings from [IndiaMART](https://www.indiamart.com/), a major B2B platform. The solution is designed for scalability, reliability, and ease of orchestration using modern data engineering tools.

---

## Objective

Extract, process, and store high-quality, structured product data from all relevant categories and sub-categories on IndiaMART. The pipeline is designed to be robust, reproducible, and extensible for future data engineering needs.

---

## Data Architecture

**Overview:**

- **Input:** List of top-level category URLs (`targets.txt`)
- **Scraping:** Multi-stage Scrapy spiders extract categories, sub-categories, sub-sub-categories, and product listings.
- **Intermediate Storage:** All intermediate and final outputs are stored as JSON in a shared data volume (`$DATA`).
- **Orchestration:** Apache Airflow DAG coordinates the scraping workflow.
- **Processing:** (Planned) PySpark jobs for data cleaning and transformation.
- **Storage:** PostgreSQL database for structured, queryable product data.

**Pipeline Flow:**

1. **Category Extraction:**  
   [`IndiaMartCategory`](IndiaMart/spiders/IndiaMartCategory.py) spider reads `targets.txt` and extracts sub-categories.
2. **Sub-Category Extraction:**  
   [`IndiaMartSubCategory`](IndiaMart/spiders/IndiaMartSubCategory.py) spider reads sub-category JSON and extracts sub-sub-categories.
3. **Product Extraction:**  
   [`IndiaMartProduct`](IndiaMart/spiders/IndiaMartProduct.py) spider reads sub-sub-category JSON and extracts product listings.
4. **(Planned) Processing:**  
   PySpark jobs (to be implemented) will clean and normalize the data before loading into PostgreSQL.
5. **Orchestration:**  
   The entire workflow is orchestrated by an Airflow DAG ([`IndiaMartScraper.py`](orchastration/dags/IndiaMartScraper.py)), running in Docker Compose.

---

## Technology & Design Justification

- **Scrapy + BeautifulSoup:**  
  Scrapy provides a robust, asynchronous scraping framework with built-in support for retries, throttling, and extensibility. BeautifulSoup is used for flexible HTML parsing, especially for complex or irregular page structures.
- **Apache Airflow:**  
  Chosen for its mature DAG-based orchestration, scheduling, and monitoring capabilities. Airflow enables reproducible, auditable ETL pipelines and integrates well with Docker.
- **Docker Compose:**  
  Ensures consistent, reproducible environments for development and deployment. All services (Airflow, Scrapy, PostgreSQL, Redis) are containerized for isolation and portability.
- **PostgreSQL:**  
  Reliable, open-source relational database for storing structured product data, supporting complex queries and analytics.
- **PySpark:**  
  (Planned) For scalable, distributed data processing and cleaning, especially as data volumes grow.
- **Redis:**  
  Used as a broker for Airflow's CeleryExecutor, enabling distributed task execution.
- **Filesystem-based Data Exchange:**  
  All intermediate files are stored in a shared Docker volume (`$DATA`), simplifying data flow between pipeline stages and supporting easy debugging.

**Development Approach:**

- **Modular Spiders:**  
  Each spider is responsible for a single stage, making the pipeline easy to debug and extend.
- **Configurable Inputs/Outputs:**  
  All file paths are parameterized and mapped via Docker volumes, supporting local development and production deployment.
- **Environment-Driven Configuration:**  
  All credentials and paths are managed via `.env` and injected into containers, supporting secure and flexible deployments.
- **Open Source & Reproducibility:**  
  All infrastructure is defined as code (Docker, Airflow DAGs, SQL init scripts), ensuring anyone can reproduce the pipeline.

---

## Setup

### 1. Environment Configuration (`.env`)

Set the following environment variables in a `.env` file at the root of the project. If not set, defaults from [`build.sh`](build.sh) will be used.

#### Airflow Settings

| Variable                             | Default                          | Description                                |
|--------------------------------------|----------------------------------|--------------------------------------------|
| `AIRFLOW_ADMIN_EMAIL`                | `admin@example.com`              | Admin email                                |
| `AIRFLOW_ADMIN_FIRST_NAME`           | `Administrator`                  | Admin first name                           |
| `AIRFLOW_ADMIN_LAST_NAME`            | `System`                         | Admin last name                            |
| `AIRFLOW_ADMIN_PASSWORD`             | `admin`                          | Admin password                             |
| `AIRFLOW_ADMIN_USERNAME`             | `admin`                          | Admin username                             |
| `AIRFLOW_WEBSERVER_SECRET_KEY`       | `airflowsecretkey`               | Flask secret key                           |
| `AIRFLOW__CELERY__RESULT_BACKEND`    | Derived                          | Result backend connection string           |
| `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN`| Derived                          | SQLAlchemy connection string               |
| `AIRFLOW_CONN_PRODUCTS_DB`           | Derived                          | Connection string for product database     |

#### Data Pipeline Settings

| Variable                             | Default                          | Description                                |
|--------------------------------------|----------------------------------|--------------------------------------------|
| `DATA`                               | `./data`                         | Directory for staging inputs and outputs   |

#### PostgreSQL Settings

| Variable                             | Default                          | Description                                |
|--------------------------------------|----------------------------------|--------------------------------------------|
| `POSTGRES_AIRFLOW_DATABASE`          | `airflow`                        | Database for Airflow metadata              |
| `POSTGRES_AIRFLOW_PASSWORD`          | `airflowpassword`                | Password for Airflow database              |
| `POSTGRES_AIRFLOW_USERNAME`          | `airflow`                        | Username for Airflow database              |
| `POSTGRES_PRODUCTS_DATABASE`         | `products`                       | Database for storing scraped product data  |
| `POSTGRES_PRODUCTS_PASSWORD`         | `productsdatabasepassword`       | Password for product database              |
| `POSTGRES_PRODUCTS_USERNAME`         | `products`                       | Username for product database              |
| `POSTGRES_USERNAME`                  | `postgres`                       | Root PostgreSQL user                       |
| `POSTGRES_PASSWORD`                  | `postgrespassword`               | Root PostgreSQL password                   |

---

### 2. Provide Input: `targets.txt`

Place a list of top-level category URLs in `./data/targets.txt` (or your configured `$DATA/targets.txt`).  
**Format:**  
- One URL per line  
- Each URL should point to a main category page on IndiaMART  
- Example:
    ```text
    https://dir.indiamart.com/industry/builders-hardware.html
    https://dir.indiamart.com/industry/medical-pharma.html
    ```

---

### 3. Build and Deploy the Pipeline

```bash
# Build containers and initialize environment
bash build.sh

# Start all services
docker compose up -d
```

---

## Orchestration: Airflow DAG

The main DAG is [`IndiaMartScraper.py`](orchastration/dags/IndiaMartScraper.py):

1. Reads `/data/targets.txt` and runs the `IndiaMartCategory` spider, outputting `/data/sub_category_output.json`.
2. Runs the `IndiaMartSubCategory` spider on `/data/sub_category_output.json`, outputting `/data/sub_sub_category_output.json`.
3. Runs the `IndiaMartProduct` spider on `/data/sub_sub_category_output.json`, outputting `/data/product_output.json`.
4. (Planned) Downstream tasks for PySpark processing and PostgreSQL loading.

All intermediate and final outputs are stored in the shared `/data` volume for easy access and debugging.

---

## Extending the Pipeline

- **Add new spiders** to [`IndiaMart/spiders`](IndiaMart/spiders) for additional data extraction.
- **Add PySpark jobs** for data cleaning and transformation in the `processor/` directory.
- **Add new Airflow DAGs** in [`orchastration/dags`](orchastration/dags) for more complex workflows.

---

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).

---