"""


Scraping Flow
-------------


1. Scrape list of all teams from autocomplete js file (~4000)
2. Retrieve every team home page and
    i. Scrape every athlete on the roster
   ii. Dispatch scrapers for all the linked meets
3. Scrape every linked meet



"""

import re

import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import Selector

from scraper.util import get_meet_tfrrs_id

class TfrrsSpider(scrapy.Spider):
    name = "tfrrs"

    homepage_url = "https://www.tfrrs.org"
    results_url = "/results_search.html"

    start_urls = [homepage_url + results_url]
    allowed_domains = ["tfrrs.org"]

    def parse_results_page(self, response: HtmlResponse):
        """
        Starting place for TFRRS scraping.
        Dispatches scrapers for recent meets and then goes to the next page of results.
        """
        # dispatch parse methods for recent meets
        yield from response.follow_all(css="td a", callback=self.parse_meet)

        # go to next page of results if it exists
        if next_button := response.css("li a[rel='next']").get():
            yield response.follow(next_button, callback=self.parse_results_page)

        self.logger.info("Scraping complete!")

    parse = parse_results_page  # alias to comply with Spider specification

    def parse_meet(self, response: HtmlResponse):
        """
        General method to parse meet.
        Dispatches the correct XC/T&F parsing method.
        """
        is_xc = re.search(r"/xc/", response.url)

        if is_xc:
            yield from self.parse_xc_meet(response)
        else:
            yield from self.parse_tf_meet(response)

    def parse_xc_meet(self, response: HtmlResponse):
        """Method for parsing an XC meet."""
        # TODO: implement

        # extract meet information and yield meet object
        header = response.css(".xc-header-row")
        date, location = header.css(".panel-heading-normal-text::text").getall()
        attributes = dict(
            span_text.split(": ")
            for span_text
            in header.css("span::text")[1:].getall()
        )  # fmt: skip

        yield {
            "idTFRRS": get_meet_tfrrs_id(response.url),
            "isXC": True,
            "name": response.css(".xc-heading h3::text").get(),
            "date": date,
            "location": location,
            "attributes": attributes,
        }

        race_links: list[Selector] = response.css(".event-links + ol a")
        for link in race_links:
            race_id = link.css("::attr(href)").re(r"#(.+)")
            race_name = link.css("::text")
            attributes = {"race_id": race_id, "race_name": race_name}

            # select the second .row after the anchor (the first is team results)
            individual_results_row = response.css(f"a[name='{link}'] + .row + .row")

            yield from self.parse_xc_race(individual_results_row, attributes=attributes)

    def parse_xc_race(self, row: Selector, attributes={}):
        """
        Method for parsing a specific race within an XC meet.
        E.g. the men's 8k within Carleton Running of the Cows
        """
        title = row.css("h3::text").re(".+(?= Individual Results)")
        distance = row.css("h3::text").re(r".+\((.+)\)")  # TODO: convert to meters
        gender = "women" in title.lower()

        yield attributes | {
            ""
        }


        # TODO: parse results
        for tr in row.css("tr"):
            yield {
                "idTFRRS": None,
                
            }


    # TODO: low priority methods to implement

    def parse_tf_meet(self, response: HtmlResponse):
        """Method for parsing a T&F meet."""
        pass

    def parse_tf_event(self, response: HtmlResponse):
        pass
