"""Utility functions for extracting data from TFRRS."""
import re
from datetime import datetime
import requests
import re
import json

from scrapy.selector import SelectorList
import pandas as pd

# TODO do some cleanup. a lot of these aren't needed anymore


def _clean(string: str) -> str:
    return re.sub(r"\s+", " ", string).strip()


def get_attributes(spans: SelectorList):
    return dict(span_text.split(": ") for span_text in spans.getall())


def get_meet_tfrrs_id(url: str) -> int:
    match = re.search(r"/results(/xc)?/(\d+)", url)
    return int(match.group(2))


def _get_team_id(td: str) -> str:
    if not td.a:
        return None
    return re.search(r"xc/(.+?)\.html", td.a["href"]).group(1)


def _fmt_time(td: str) -> float:
    """Returns time in seconds, `None` if DNF/DNS."""
    string = _clean(td.text)

    if string.upper() in ["DNS", "DNF", "DQ", "SCR", "NT"]:
        return None

    string, tenths = string.split(".") if "." in string else (td.text, 0)
    time = reversed([int(i) for i in string.split(":") + [tenths]])

    multipliers = [0.1, 1, 60, 60 * 60]

    return sum(m * t for m, t in zip(multipliers, time))


def _fmt_place(td) -> int:
    string = _clean(td.text)
    if not string:
        return None

    return int(string)


def _fmt_date(string: str) -> int:
    """Converts dat to format `DD/MM/YY`"""
    string = _clean(string)
    try:
        date_obj = datetime.strptime(string, "%B %d, %Y")
    except ValueError:
        month, day = [int(s) for s in string.strip("()").split("/")]
        date_obj = datetime(2021, month, day)

    return date_obj.strftime("%m/%d/%Y")


def get_meets_df() -> pd.DataFrame:
    """Retrieves information for every meet on TFRRS via a public
    direct athletics script and format it as a pandas DataFrame"""

    url = "https://www.directathletics.com/scripts/fuseDriver.js"
    headers = {"user-agent": "jfrrs"}  # server rejects requests without this

    with requests.get(url, headers=headers) as r:
        assert r.status_code == 200, "Request rejected by Direct Athletics"
        js = r.text.replace("\t", " ")

    # regex pattern to find the json array in the .js file
    pattern = re.compile(r"(\[\s*(?:{.+?},?\s*)*\]);", flags=re.DOTALL)

    raw_array_string = pattern.search(js).group(1)
    meets = pd.DataFrame(json.loads(raw_array_string))

    # convert dates to python datetimes
    meets["date_begin"] = pd.to_datetime(
        meets["date_begin"], infer_datetime_format=True
    )

    # drop non-tfrrs meets
    meets = meets[meets.tfrrs == "1"]

    # convert sport to one of itf, otf, xc
    meets["sport"] = [
        sport if sport != "track" 
        else ("otf" if outdoors == "1" else "itf")
        for sport, outdoors in zip(meets.sport, meets.outdoors)
    ]  # fmt: skip

    # cleanup
    meets.rename(columns={"meet_hnd": "tfrrs_id", "date_begin": "date"}, inplace=True)
    meets.drop(columns=["outdoors", "url", "tfrrs", "meetpro"], inplace=True)
    meets.reset_index(inplace=True, drop=True)

    return meets

def get_teams_df() -> pd.DataFrame:
    """"""

