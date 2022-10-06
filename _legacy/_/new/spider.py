import scrapy
import re

from pprint import pprint

from models import Athlete, Meet, Result


class TRFFRSScraper(scrapy.Spider):
    name = "TFRRS Scraper"
    start_urls = [
        "https://www.tfrrs.org/results/xc/19000/NCAA_Division_III_Metro_Region_Cross_Country_Championships",
    ]

    def parse(self, response):

        meet_info = parse_meet(response)

        meet_id = meet_info.id

        tables = response.css("table")

        parse_table(tables[1])

    # TODO:
    # - scrape results




def parse_meet(response) -> Meet:
    pass

def parse_table(table: scrapy.Selector):
    columns = [t.strip().lower() for t in table.css("thead th::text").getall()]

    print(columns)
    for row in table.css("tbody tr"):
        cols = dict(zip(columns, row.css("td div")))
        last_name, first_name = cols["name"].css("a::text").get().split(", ")
        meet_id = None
        race_id = None
        result = Result(
            meet_id=meet_id,
            race_id=race_id,
            athlete_id=cols["name"].xpath("a/@href").re_first(r"/(\d+)"),
            team_id=cols["team"].xpath("a/@href").re_first(r"xc/(.+?)\.html"),
            last_name=last_name,
            first_name=first_name,
        )

        pprint(result)

