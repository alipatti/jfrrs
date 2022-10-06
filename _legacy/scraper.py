import re
from datetime import datetime
from typing import Any, Callable, Iterable
import pandas as pd

import requests
import bs4


def get_meet_url(meet_id: int) -> str:
    return f"https://www.tfrrs.org/results/xc/{meet_id}"


####################
# HELPER FUNCTIONS #
####################


def _clean(string: str) -> str:
    return re.sub(r"\s+", " ", string).strip()


def _get_dist(table_title: str) -> int:
    raw = re.findall(r"\((.+?)\)", table_title)[-1].strip().lower()
    multiplier = 1

    if "k" in raw:
        raw = raw.replace("k", "")
        multiplier *= 1000

    if "mile" in raw:
        raw = raw.replace("mile", "")
        multiplier *= 1609

    return int(float(raw) * multiplier)


def _get_tfrrs_id(td: str) -> int:
    if not td.a:
        return None
    return int(re.search(r"/(\d+)", td.a["href"]).group(1))


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


def _find_mens_results(soup: bs4.BeautifulSoup) -> tuple[bs4.BeautifulSoup, str]:
    """
    Finds men's individual results table within TFRRS meet page.
    """
    for div in soup.find_all("div", "custom-table-title-xc"):
        title = _clean(div.text.lower().replace("'", ""))
        if "men" in title and "indiv" in title and "women" not in title:
            return div.find_next_sibling("table"), _get_dist(title)

    return None, None


def _parse_cols(
    table: bs4.BeautifulSoup,
    col_parsers: list[tuple[str, str, Callable[[bs4.Tag], Any]]],
) -> Iterable[dict]:
    """
    Parse columns of bs4.BeautifulSoup table using provided functions.

    ```
    col_parsers = [
        (dict key, name of column in html table, processing function),
        ...
    ]
    ```
    """

    header_row = table.find("tr").find_all("th")
    column_names = [th.text.strip().lower() for th in header_row]

    rows = [row.find_all("td") for row in table.find_all("tr")[1:]]

    cols = list(zip(*rows))
    assert len(cols) == len(column_names)
    cols = dict(zip(column_names, cols))

    for i, _ in enumerate(rows):
        yield {
            output_name: f(cols[html_col_name][i]) 
            for output_name, html_col_name, f in col_parsers
        }  # fmt: skip


def scrape_meet(tfrrs_id: int) -> tuple[dict, list[dict]]:
    """Scrapes a meet given by a TFRRS id.
    Returns meet info as a dictionary, and the results of the meet as a list of tuples."""
    meet_url = get_meet_url(tfrrs_id)
    request = requests.get(meet_url)
    soup = bs4.BeautifulSoup(request.content, "lxml")

    name = soup.find("div", "xc-heading").text
    date, location = soup.find("div", "xc-header-row").text.split("|")
    venue, city, *_ = location.strip().split("\n")
    results_table, dist = _find_mens_results(soup)

    meet_info = {
        "id": tfrrs_id,
        "name": _clean(name),
        "date": _fmt_date(date),
        "distance": dist,
        "venue": _clean(venue),
        "location": _clean(city),
    }

    if not results_table:
        print(f"Unable to find men's results table: {_clean(name)}")
        return meet_info, None

    columns = [
        ("athlete_id", "name", _get_tfrrs_id),
        ("athlete_lastname", "name", lambda td: td.text.split(", ")[0].strip()),
        ("athlete_firstname", "name", lambda td: td.text.split(", ")[1].strip()),
        ("team_name", "team", lambda td: td.text.strip()),
        ("team_id", "team", _get_team_id),
        ("time", "time", _fmt_time),
        ("score", "score", _fmt_place),
    ]

    results = _parse_cols(results_table, columns)

    return meet_info, results


def recent_meets() -> Iterable[dict]:
    """
    Scrapes names and ids of recent XC meets from TFRRS main results page.
    Returns stream of `(meet_name, TFRRS_id)` pairs.
    """

    # load page html and show hidden content
    url = "https://www.tfrrs.org/results_search.html"
    payload = {"sport": "xc"}
    with requests.post(url, payload) as r:
        html = r.text.replace("display:none", "")

    table = bs4.BeautifulSoup(html, "lxml").find("table")
    cols = [
        ("name", "meet", lambda tr: tr.text.strip()),
        ("id", "meet", _get_tfrrs_id),
    ]

    return map(lambda info: (info["name"], info["id"]), _parse_cols(table, cols))


def test_scraping():
    from pprint import pprint

    info, results = scrape_meet(18785)  # running of the cows
    pprint(info)
    print(pd.DataFrame.from_records(results).head(10))


if __name__ == "__main__":
    # meets = get_recent_meets()
    # pprint(meets[:20])
    # print(len(meets))
    test_scraping()
