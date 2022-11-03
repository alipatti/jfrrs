"""


Scraping Flow
-------------
 1. Scrape client-side javascript files from TFRRS and DirectAthletics to get
    all teams, meets, and conferences.
 2. Add all teams/conferences that aren't already in the database.
 3. For every meet that hasn't yet been scraped
     i. Dispach a scraper to 


"""
import re
import json
from typing import TYPE_CHECKING, Literal

import scrapy
import json5  # a slower but more flexible json parser for javascript objects
import pandas as pd
import numpy as np

if TYPE_CHECKING:
    from scrapy.http import HtmlResponse, TextResponse
    from scrapy.selector import Selector


class TfrrsSpider(scrapy.Spider):  # pylint: disable=abstract-method
    name = "TFRRS Scraper"

    allowed_domains = ["tfrrs.org"]

    ##################
    # STARTING POINT #
    ##################

    def start_requests(self):
        """Dispatches requests to directathletics and tfrrs client-side
        javascript files that contain lists of all the meets, teams,
        and conferences in the database."""

        # tfrrs autocomplete script
        tfrrs_js_url = "https://www.tfrrs.org/js/navbar_autocomplete.js"

        yield scrapy.Request(
            url=tfrrs_js_url,
            callback=self.parse_tfrrs_js,
        )

        # directathletics script
        da_js_url = "https://www.directathletics.com/scripts/fuseDriver.js"
        da_headers = {"user-agent": "jfrrs"}  # server rejects requests without this

        yield scrapy.Request(
            url=da_js_url,
            callback=self.parse_directathletics_js,
            headers=da_headers,
        )

    ##################################
    # CLIENT-SIDE JAVASCRIPT PARSING #
    ##################################

    def parse_directathletics_js(self, response: "TextResponse"):
        """Extracts a list of information about all meets in the TFRRS
        database and dispatches requests to scrape them if they have
        not already been scraped.
        """

        # regex pattern to find the json array in the .js file
        pattern = re.compile(r"(\[\s*(?:{.+?},?\s*)*\]);", flags=re.DOTALL)

        javascript = response.text.replace("\t", " ")  # json parser doesn't like tabs
        raw_array_string = pattern.search(javascript).group(1)  # find the array
        meets = pd.DataFrame(json.loads(raw_array_string))  # convert to df

        # convert to python datetimes
        meets["date"] = pd.to_datetime(meets.date_begin, infer_datetime_format=True)

        # NOTE: this indoor/outdoor field is wrong for a lot of the earlier meets
        meets["outdoors"] = meets.outdoors == "1"
        meets[meets.sport == "xc"]["outdoors"] = np.nan

        meets = meets[meets.tfrrs == "1"]  # drop meets not on tfrrs

        # cleanup
        meets = (
            meets
            .rename(columns={"meet_hnd": "idTFRRS", "venue_state": "state"})
            .drop(columns=["url", "tfrrs", "meetpro", "date_begin"])
            .sort_values(["date"], ascending=False)  # most recent first
            .reset_index(drop=True)
        )  # fmt: skip

        callbacks = {
            "xc": self.parse_xc_meet,
            "track": self.parse_tf_meet,
        }

        # for debugging
        meets = meets[meets.sport == "xc"].head(10)

        for meet in meets.itertuples(index=False):
            meet_in_database = False  # TODO
            if meet_in_database:
                continue

            url = tfrrs_url_from_id(meet.idTFRRS, sport=meet.sport)
            callback = callbacks[meet.sport]
            callback_kwargs = dict(meet_info=meet._asdict())
            yield scrapy.Request(url=url, callback=callback, cb_kwargs=callback_kwargs)

    def parse_tfrrs_js(self, response: "TextResponse"):

        # extract conferences
        conferences_raw = df_from_tfrrs_js_response(
            response, "autocomplete_conferences"
        )
        conferences_columns = [
            conferences_raw.text.rename("name"),
            conferences_raw.url.str.extract(r"/leagues/(?P<idTFRRS>\d+)\.html"),
        ]
        conferences = pd.concat(
            objs=conferences_columns,
            axis="columns",
        )

        yield from conferences.to_dict("records")

        # extract teams
        teams_raw = df_from_tfrrs_js_response(response, "autocomplete_teams")
        teams_columns = [
            teams_raw.text.str.extract(r"(?P<name>.+?) \((?P<gender>[MF])\)"),
            teams_raw.url.str.extract(r"/teams/(?:tf|xc)/(?P<idTFRRS>.+)\.html"),
            teams_raw.url.str.extract(
                r"/teams/(?:tf|xc)/(?P<state>.{2})_(?P<level>.*?)_.*"
            ),
        ]
        teams = pd.concat(
            objs=teams_columns,
            axis="columns",
        )

        yield from teams.to_dict("records")

    #############################
    # MEET RESULTS PAGE PARSING #
    #############################

    def parse_xc_meet(self, response: "HtmlResponse", meet_info):
        """Method for parsing an XC meet."""

        header = response.css(".xc-header-row > div > div")

        # name, date, and idTFRRS are already in `meet_info`
        meet_info["sport"] = "xc"
        meet_info["location"] = parse_location(
            header.xpath("./div/div/text()")[-1].get()
        )
        meet_info["attributes"] = parse_meet_attributes(header)

        # parse individual races
        races = self.parse_xc_races(response)

        # break

        meet_info["events"] = {"create": races}  # for prisma write

        yield meet_info

    def parse_xc_races(self, response: "HtmlResponse") -> list[dict]:
        # hyperlinks to jump to individual events in the meet
        race_links: list["Selector"] = response.css(".event-links + ol a")

        races = []
        for link in race_links:
            race_info = {}
            race_info["name"] = link.xpath("./text()").get()

            # HACK... but all my simpler solutions break
            # pylint: disable=line-too-long
            title_div = response.xpath(
                f'//*[.//*[contains(text(), "Individual Results") and contains(text(), "{race_info["name"]}")] and contains(@class, "custom-table-title")]'
            )

            results_table = title_div.xpath("./following-sibling::table[1]")
            results = self.parse_xc_results(results_table)

            race_info["idTFRRS"] = int(link.css("::attr(href)").re(r"#event(\d+)")[0])
            race_info["distance"] = parse_distance(
                title_div.css("h3::text").re_first(r".+\((.+)\)")
            )
            race_info["gender"] = "W" if "women" in race_info["name"].lower() else "M"

            race_info["results"] = {"create": results}  # for prisma write

            races.append(race_info)

        return races

    def parse_xc_results(self, results_table: "Selector") -> list[dict]:
        """
        Method for parsing a specific race within an XC meet.
        E.g. the men's 8k within Carleton Running of the Cows

        Yields one `meet` item and lots of `result` items
        """

        results = []
        for tr in results_table.xpath("./tbody/tr"):
            result_info = {}

            tds = {
                col_name.lower(): td
                for col_name, td in zip(
                    results_table.xpath("./thead/tr/th/text()").re(r"(.+)\s*"),
                    tr.xpath("./td"),
                )
            }

            result_info["place"] = parse_score(tds["pl"].xpath("text()").get())
            result_info["time"] = parse_time(tds["time"].xpath("text()").get())
            result_info["score"] = parse_score(tds["score"].xpath("text()").get())
            result_info["classYear"] = parse_class_year(
                tds["year"].xpath("text()").get()
            )

            result_info["athleteId"] = athlete_id_from_td(tds["name"])
            result_info["teamId"] = team_id_from_td(tds["team"])

            results.append(result_info)

        return results

    def parse_tf_meet(self, response: "HtmlResponse"):
        # TODO
        return {}


###########
# HELPERS #
###########

# IMPROVEMENT
# move this logic into an item pipeline?
# the problem is how do we group data to insert as one big prisma query
# per meet once we send stuff down the pipeline


def df_from_tfrrs_js_response(response: "HtmlResponse", variable_name: str):
    regex_pattern = re.compile(
        rf"{variable_name}\s*=\s*(\[.+?\]);",
        flags=re.DOTALL,
    )
    raw_array_string = regex_pattern.search(response.text).group(1)
    return pd.DataFrame(json5.loads(raw_array_string))


def tfrrs_url_from_id(idTFRRS: int, sport: Literal["xc", "tf"]):
    return f"https://tfrrs.org/results{'/xc' if sport == 'xc' else ''}/{idTFRRS}"


def athlete_id_from_td(td: "Selector") -> int | None:
    idTFRRS = td.xpath("./a/@href").re_first(r".+/athletes/(\d+?)/")
    return int(idTFRRS) if idTFRRS else None


def team_id_from_td(td: "Selector") -> str | None:
    return td.xpath("./a/@href").re_first(r".+/teams(?:/xc)?/(\w+)\.html")


#####################
# PARSING FUNCTIONS #
#####################


def parse_time(string: str) -> float:
    if string.upper() in {"DNS", "DNF", "DQ"}:
        return None

    whole, fractional = string.split(".") if "." in string else (string, 0)

    seconds = sum(
        mult * int(value)
        for mult, value in zip(
            [1, 60, 60 * 60],
            reversed(whole.split(":")),
        )
    )

    seconds += float(f"0.{fractional}")

    return seconds


def parse_score(string: str) -> int:
    if string is None:
        return None

    return int(string)


def parse_class_year(string: str) -> Literal["FR", "SO", "JR", "SR"]:
    if string in {"\xa0"}:  # non-breaking space
        return None

    year = string[:2]  # HACK

    if year in {"FR", "SO", "JR", "SR"}:
        return year

    return None


def parse_distance(string) -> float:
    """in meters"""

    string = string.lower()
    multiplier = 1

    if "k" in string:
        string = string.replace("k", "")
        multiplier *= 1000

    if "mile" in string:
        string = string.replace("mile", "")
        multiplier *= 1609

    return float(string) * multiplier


def parse_location(string: str) -> str:
    return clean_whitespace(string)


def parse_meet_attributes(header: "Selector"):
    return dict(
        span_text.split(": ") for span_text in header.xpath("./span/text()").getall()
    )


########
# MISC #
########


def clean_whitespace(string: str) -> str:
    return re.sub(r"\s+", " ", string.strip())
