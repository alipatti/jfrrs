"""Utility functions for extracting data from TFRRS."""
import re
import requests
import re

import json
import json5  # a slower but more flexible json parser to javascript objects
import pandas as pd


# NOTE: KEEP DF COLUMN NAMES CONSISTENT WITH PRISMA SCHEMA FOR EASIER INTEGRATION


def get_meets_df() -> pd.DataFrame:
    """Retrieves information for every meet on TFRRS via a client-side
    direct athletics script and format it as a pandas DataFrame"""

    url = "https://www.directathletics.com/scripts/fuseDriver.js"
    headers = {"user-agent": "jfrrs"}  # server rejects requests without this

    with requests.get(url, headers=headers) as r:
        assert r.status_code == 200, "Request rejected"
        js = r.text.replace("\t", " ")

    # regex pattern to find the json array in the .js file
    pattern = re.compile(r"(\[\s*(?:{.+?},?\s*)*\]);", flags=re.DOTALL)

    raw_array_string = pattern.search(js).group(1)
    meets = pd.DataFrame(json.loads(raw_array_string))

    # convert dates to python datetimes
    meets["date_begin"] = pd.to_datetime(meets.date_begin, infer_datetime_format=True)

    meets["outdoors"] = meets.outdoors == "1"  # some of these are just wrong...

    # drop non-tfrrs meets
    meets = meets[meets.tfrrs == "1"]

    # cleanup
    meets.rename(columns={"meet_hnd": "idTFRRS", "date_begin": "date"}, inplace=True)
    meets.drop(columns=["url", "tfrrs", "meetpro"], inplace=True)
    meets.reset_index(inplace=True, drop=True)

    return meets


def get_teams_df() -> pd.DataFrame:
    """Extracts team information from TFRRS autocomplete script."""
    raw_df = _fetch_autocomplete_data(table_name="autocomplete_teams")

    # extract meaningful information
    columns = [
        raw_df.text.str.extract(r"(?P<name>.+?) \((?P<gender>[MF])\)"),
        raw_df.url.str.extract(r"/teams/(?:tf|xc)/(?P<idTFRRS>.+)\.html"),
        raw_df.url.str.extract(r"/teams/(?:tf|xc)/(?P<state>.{2})_(?P<level>.*?)_.*"),
    ]

    return pd.concat(objs=columns, axis="columns")  # combine into df and return


def get_conferences_df() -> pd.DataFrame:
    """Extracts conference information from TFRRS autocomplete script."""

    raw_df = _fetch_autocomplete_data(table_name="autocomplete_conferences")

    columns = [
        raw_df.text.rename("name"),
        raw_df.url.str.extract(r"/leagues/(?P<idTFRRS>\d+)\.html"),
    ]

    return pd.concat(objs=columns, axis="columns")


def _fetch_autocomplete_data(table_name):
    """Helper method. See above."""

    # fetch js file
    url = "https://www.tfrrs.org/js/navbar_autocomplete.js"
    with requests.get(url) as r:
        javascript = r.text

    # find desired array and return it as a dataframe
    regex_pattern = re.compile(rf"{table_name}\s*=\s*(\[.+?\]);", flags=re.DOTALL)
    raw_array_string = regex_pattern.search(javascript).group(1)
    return pd.DataFrame(json5.loads(raw_array_string))
