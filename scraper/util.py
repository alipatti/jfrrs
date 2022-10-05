"""Utility functions for extracting data from TFRRS."""
from scrapy.http import HtmlResponse
from scrapy.selector import SelectorList
import re
from datetime import datetime


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
