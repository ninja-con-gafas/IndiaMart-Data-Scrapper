from bs4 import BeautifulSoup
from json import loads
from scrapy import Request, Spider
from scrapy.http import Response
from re import DOTALL, search
from typing import Dict, Generator
from urllib.parse import urljoin

class IndiaMartSubCategory(Spider):
    """
    Scrapy Spider to extract subsubcategories from the subcategory of goods directory of IndiaMART. 

    Reads subcategory URLs from a text file and scrapes subsubcategory `name`, `fname`, `brand_name` and `prod-map-total`.

    Attributes:
        base_url (str): Base URL for the IndiaMART sub-subcategory.
        name (str): Unique spider name used by Scrapy to identify this spider.
        path (str): Path to the file containing target subcategory URLs.
    """

    name = "IndiaMartSubCategory"

    def __init__(self, base_url: str = "https://dir.indiamart.com/impcat/", path: str = "targets.txt"):
        """
        Initialize the spider with a path to the input file.

        Parameters:
            base_url (str): Base URL for the IndiaMART sub-subcategory.
            path (str): Path to the file containing subcategory URLs.
        """

        self.path = path
        self.base_url = base_url


    def start_requests(self):
        """
        Reads target category URLs from text file and sends Scrapy requests.

        Yields:
            Request: Scrapy Request objects with category URLs and associated metadata.
        """

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                urls = [url.strip() for url in file.readlines() if url.strip()]
                for url in urls:
                    yield Request(
                        url=url,
                        callback=self.parse,
                        meta={"category_url": url},
                        dont_filter=True
                    )
        except FileNotFoundError:
            self.logger.error(f"{self.path} file not found.")

    def parse(self, response: Response) -> Generator[Dict[str, str], None, None]:
        """
        Parses subsubcategories data from the IndiaMART subcategories.

        Parameters:
            response (Response): The response object.

        Yields:
            dict: A dictionary containing:
                - sub_sub_category (str): Sub-subcategories name.
                - sub_sub_category_brand_name (str): Brand name of the sub-subcategory.
                - sub_sub_category_prod_map_total (str): Total number of products in the sub-subcategory.
                - sub_sub_category_url (str): Fully resolved URL for the sub-subcategory.
        """

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
                    return None
                    
                json_str = match.group(1)
                initial_state: Dict = loads(json_str)

        mcats = initial_state.get("mcats", [])
        if not mcats:
            self.logger.warning(f"No 'mcats' data found in the JSON for {response.url}")
            return None
        
        self.logger.info(f"Found {len(mcats)} sub-subcategories in the JSON data.")
        for mcat in mcats:
            sub_sub_category = mcat.get("name")
            sub_sub_category_brand_name = mcat.get("brand_name")
            sub_sub_category_prod_map_total = mcat.get("prod_map_total")
            sub_sub_category_url = urljoin(self.base_url, f"{mcat.get('fname')}.html")

            yield {
                "sub_sub_category": sub_sub_category,
                "sub_sub_category_brand_name": sub_sub_category_brand_name,
                "sub_sub_category_prod_map_total": sub_sub_category_prod_map_total,
                "sub_sub_category_url": sub_sub_category_url
            }
