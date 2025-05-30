from bs4 import BeautifulSoup
from json import loads
from scrapy import Request, Spider
from scrapy.http import Response
from re import DOTALL, search
from typing import Dict, Generator
from urllib.parse import urljoin

class IndiaMartSubCategory(Spider):
    """
    Scrapy Spider to extract sub-sub-categories from the sub-category of goods directory of IndiaMART. 

    Reads sub-category URLs from a JSON file and scrapes sub-sub-category `name`, `fname`, `brand_name` and `prod-map-total`.

    Attributes:
        base_url (str): Base URL for the IndiaMART sub-sub-category.
        name (str): Unique spider name used by Scrapy to identify this spider.
        path (str): Path to the JSON file containing:
                        - category (str): Main category name.
                        - sub_category (str): Sub-category name.
                        - sub_category_url (str): Fully resolved URL for the sub-category.
    """

    name = "IndiaMartSubCategory"

    def __init__(self, base_url: str = "https://dir.indiamart.com/impcat/", path: str = "targets.txt"):
        """
        Initialize the spider with a path to the input file.

        Parameters:
            base_url (str): Base URL for the IndiaMART sub-sub-category.
            path (str): Path to the JSON file containing:
                        - category (str): Main category name.
                        - sub_category (str): Sub-category name.
                        - sub_category_url (str): Fully resolved URL for the sub-category.
        """

        self.path = path
        self.base_url = base_url


    def start_requests(self):
        """
        Reads target category URLs from a JSON file and sends Scrapy requests.

        Yields:
            Request: Scrapy Request objects with category URLs and associated metadata.
        """

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                targets = loads(file.read())

                for target in targets:
                    category = target.get("category")
                    sub_category = target.get("sub_category")
                    sub_category_url = target.get("sub_category_url")

                    if not (category and sub_category and sub_category_url):
                        self.logger.warning(f"Skipping incomplete entry: {target}")
                        continue

                    yield Request(
                        url=sub_category_url,
                        callback=self.parse,
                        meta={
                            "category": category,
                            "sub_category": sub_category,
                            "sub_category_url": sub_category_url
                        },
                        dont_filter=True
                    )
        except FileNotFoundError:
            self.logger.error(f"{self.path} file not found.")
        except Exception as e:
            self.logger.error(f"Failed to parse {self.path}: {e}")

    def parse(self, response: Response) -> Generator[Dict[str, str], None, None]:
        """
        Parses sub-sub-categories data from the IndiaMART sub-categories.

        Parameters:
            response (Response): The response object.

        Yields:
            dict: A dictionary containing:
                - category (str): Main category name.
                - sub_category (str): Sub-category name.
                - sub_sub_category (str): Sub-sub-category name.
                - sub_sub_category_brand_name (str): Brand name of the sub-sub-category, if applicable.
                - sub_sub_category_prod_map_total (str): Total number of products in the sub-sub-category.
                - sub_sub_category_url (str): Fully resolved URL for the sub-sub-category.
        """

        category = response.meta.get("category")
        sub_category = response.meta.get("sub_category")

        soup = BeautifulSoup(response.text, "lxml")
        script_tags = soup.find_all('script')

        for script in script_tags:
            if script.string and 'window.__INITIAL_STATE__' in script.string:
                match = search(
                    r'window\.__INITIAL_STATE__\s* = \s*({.*?});',
                    script.string,
                    DOTALL
                )
                if not match:
                    self.logger.warning(f"No JSON data found in the script tags for {response.url}")
                    return

                json_str = match.group(1)
                initial_state: Dict = loads(json_str)
                break
        else:
            self.logger.warning(f"No '__INITIAL_STATE__' script tag found for {response.url}")
            return

        mcats = initial_state.get("mcats", [])
        if not mcats:
            self.logger.warning(f"No 'mcats' data found in the JSON for {response.url}")
            return

        self.logger.info(f"Found {len(mcats)} sub-sub-categories in the JSON data.")
        for mcat in mcats:
            sub_sub_category = mcat.get("name")
            sub_sub_category_brand_name = mcat.get("brand_name")
            sub_sub_category_prod_map_total = mcat.get("prod-map-total")
            sub_sub_category_url = urljoin(self.base_url, f"{mcat.get('fname')}.html")

            yield {
                "category": category,
                "sub_category": sub_category,
                "sub_sub_category": sub_sub_category,
                "sub_sub_category_brand_name": sub_sub_category_brand_name,
                "sub_sub_category_prod_map_total": sub_sub_category_prod_map_total,
                "sub_sub_category_url": sub_sub_category_url
            }
