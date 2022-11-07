import os
from typing import TYPE_CHECKING
import requests

from dotenv import load_dotenv

if TYPE_CHECKING:
    from scraper.spider import TfrrsSpider

load_dotenv()

API_URL = f"{os.getenv('APP_URL')}/api/db"
API_KEY = os.getenv("SCRAPER_API_KEY")


class SaveToDatabase:
    def process_item(self, item, spider: "TfrrsSpider"):

        # send data off to the site
        with requests.post(API_URL, data=item, timeout=10) as r:
            if r.status_code != 200:
                spider.logger.error("TODO")
