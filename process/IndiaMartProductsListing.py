from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import array_sort, col, collect_set, concat_ws, size, trim, udf
from pyspark.sql.types import DoubleType, IntegerType, StringType
from typing import Optional

class IndiaMartProductsListing:
    """
    Cleans and deduplicates IndiaMart product listing data using PySpark.

    Parameters:
        input_path (str): Path to the input JSON file.

    Attributes:
        products (DataFrame): The DataFrame containing list of products.

    Methods:
        run(): Executes the full cleaning and deduplication.
    """

    def __init__(self, input_path: str):
        self.input_path = input_path

    def _clean_and_transform(self, products: DataFrame) -> DataFrame:
        """
        Performs data cleaning by trimming strings and casting data types. It cleans price fields using a UDF and
        filters out invalid prices.

        Parameters:
            products (DataFrame): DataFrame containing list of products scraped from the indiamart.com website.

        Returns:
            DataFrame: Cleaned and transformed DataFrame with trimmed strings and cleaned prices.

        Schema:
            Cleaned products data:
                category (string): Trimmed main category.
                sub_category (string): Trimmed secondary category.
                sub_sub_category (string): Trimmed further subdivision.
                product (string): Trimmed product name.
                url (string): Trimmed URL.
                price (double): Cleaned and rounded price value.
        """
      
        def clean_price(price_text: Optional[str]) -> Optional[float]:
            """
            Cleans and converts a price string to a float. Removes currency symbols, commas, and text suffixes.

            Parameters:
                price_text (str): Raw price input string, possibly containing currency symbols and units.

            Returns:
                Optional[float]: Sanitized and rounded price as float, or None if invalid.
            """

            if not price_text or not isinstance(price_text, str):
                return None
            sanitized = price_text.replace('₹', '').replace(',', '').split('/')[0]
            sanitized = ''.join(char for char in sanitized if char.isdigit() or char == '.')
            try:
                return round(float(sanitized), 2)
            except Exception:
                return None

        clean_price_udf = udf(clean_price, DoubleType())

        return (products.withColumn("category", trim(col("category")).cast(StringType()))
                .withColumn("sub_category", trim(col("sub_category")).cast(StringType()))
                .withColumn("sub_sub_category", trim(col("sub_sub_category")).cast(StringType()))
                .withColumn("product", trim(col("product")).cast(StringType()))
                .withColumn("url", trim(col("url")).cast(StringType()))
                .withColumn("price", clean_price_udf(col("price")))
                .filter(col("price").isNotNull()))

    def _deduplicate(self, products: DataFrame) -> DataFrame:
        """
        Deduplicates product entries by grouping on product identifiers and aggregates unique sub-sub-categories into a
        single field and computes tag count.

        Parameters:
            products (DataFrame): DataFrame containing cleaned product data.

        Returns:
            DataFrame: Deduplicated DataFrame with aggregated sub-sub-categories and tag counts.

        Schema:
            Deduplicated product data:
                category (string): Main category of the product.
                sub_category (string): Secondary category under the main category.
                product (string): Product name.
                price (double): Cleaned and rounded product price.
                url (string): URL link to the product page.
                sub_sub_categories (string): Comma-separated list of unique sub-sub-categories.
                tags (int): Count of unique sub-sub-categories aggregated.
        """

        return (
            products
            .filter(col("price").isNotNull())
            .dropDuplicates(["category", "sub_category", "sub_sub_category", "product", "price", "url"])
            .groupBy("category", "sub_category", "product", "price", "url")
            .agg(array_sort(collect_set("sub_sub_category")).alias("sub_sub_categories_array"))
            .withColumn("sub_sub_categories", concat_ws(", ", col("sub_sub_categories_array")))
            .withColumn("tags", size(col("sub_sub_categories_array")))
            .drop("sub_sub_categories_array")
        )

    def run(self, spark: SparkSession) -> None:
        """
        Loads raw JSON, cleans and transforms data, removes duplicates, and registers the result as a temporary Spark 
        SQL view.

        Parameters:
            None

        Returns:
            None
        """

        self._deduplicate(
            self._clean_and_transform(
                spark.read.json(self.input_path)
                )).createOrReplaceTempView("products")
