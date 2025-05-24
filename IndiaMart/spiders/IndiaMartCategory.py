from bs4 import BeautifulSoup
from bs4.element import Tag
from scrapy import Request, Spider
from scrapy.http import Response
from typing import Dict, Generator, List
from urllib.parse import urljoin

class IndiaMartCategory(Spider):
    """
    Scrapy Spider to extract sub-categories from the goods directory of IndiaMART. 

    Reads category URLs from a text file and scrapes `category`, `sub_category`, `sub_category_url` under each category.

    Attributes:
        name (str): Unique spider name used by Scrapy to identify this spider.
        path (str): Path to the file containing target category URLs.
    """

    name = "IndiaMartCategory"

    def __init__(self, path: str = "targets.txt"):
        """
        Initialize the spider with a path to the input file.

        Parameters:
            path (str): Path to the file containing category URLs.
        """

        self.path = path

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
        Parses sub-category data from the IndiaMART directory.

        Parameters:
            response (Response): The response object.

        Yields:
            dict: A dictionary containing:
                - category (str): Main category name.
                - sub_category (str): Sub-category name.
                - sub_category_url (str): Fully resolved URL for the sub-category.
        """

        soup = BeautifulSoup(response.text, "lxml")

        category_tag = soup.find("h1")
        if not category_tag:
            self.logger.warning(f"No <h1> main category found for {response.url}")
            return

        category = category_tag.get_text(strip=True)
        self.logger.info(f"Extracting sub categories from {category} category")

        sub_categories_tag: Tag = soup.find("div", attrs={"class": "mid"})
        if not sub_categories_tag:
            self.logger.warning(f"No <ul> found following <h1> for {response.url}")
            return
        ul_tags: List = sub_categories_tag.find_all("ul")
        self.logger.info(f"Found {len(ul_tags)} <ul> tags in the sub-categories section.")

        for ul_tag in ul_tags:
            li_tags: List = ul_tag.find_all("li")
            self.logger.info(f"Found {len(li_tags)} <li> tags in the <ul> tag of the sub-categories section.")
            for li_tag in li_tags:
                sub_category_link: str = li_tag.find("a")
                if sub_category_link:
                    sub_category: str = sub_category_link.get_text(strip=True)
                    sub_category_url: str = sub_category_link.get("href")
                yield {
                    "category": category,
                    "sub_category": sub_category,
                    "sub_category_url": urljoin(response.meta["category_url"], sub_category_url)
                }