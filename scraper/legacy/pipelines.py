from typing import TYPE_CHECKING
import json
import os

from scrapy import Request
import dotenv

if TYPE_CHECKING:
    from scrapy import Spider
    from scrapy.http import TextResponse
    from scrapy.core.engine import ExecutionEngine

dotenv.load_dotenv()

API_URL = f"{os.getenv('APP_URL')}/api/scraper"
API_KEY = os.getenv("SCRAPER_API_KEY")


class SaveToDatabase:
    async def process_item(self, data, spider: "Spider"):

        # `data` must be of the type described in pages/api/scraper/insert.ts

        engine: "ExecutionEngine" = spider.crawler.engine

        data["key"] = API_KEY

        request = Request(
            url=API_URL + "/insert",
            body=json.dumps(data),
            method="POST",
            # tell Next api middleware to parse json
            headers={"Content-Type": "application/json"},
            priority=100
        )

        response: "TextResponse" = await engine.download(request)

        assert response.status == 200
