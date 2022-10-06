from pathlib import Path
import dateutil
from io import StringIO
import re

import requests
import pandas as pd


OUTPUT_FOLDER = Path("prescraping")


def get_meets() -> pd.DataFrame:
    # get javacript file from directathletics site
    url = "https://www.directathletics.com/scripts/fuseDriver.js"
    headers = {
        "authority": "www.directathletics.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9,la;q=0.8",
        "cache-control": "max-age=0",
        "cookie": "__utma=138588838.663648652.1656164692.1656164692.1656164692.1; __utmc=138588838; __utmz=138588838.1656164692.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=138588838.public",
        "dnt": "1",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    }

    with requests.get(url, headers=headers) as f:
        javascript = f.text

    # find meet array in retrieved javascript file
    pattern = r"data\s*=\s*(\[(.|\n)+?\]);"
    json = re.search(pattern, javascript).group(1).replace("\n", "")

    meets = pd.read_json(StringIO(json))  # load into dataframe

    # cleanup columns
    meets["tfrrs"] = meets.tfrrs == "1"
    meets["date"] = [dateutil.parser.parse(date) for date in meets.date_begin]

    meets = (
        meets[(meets.sport == "xc") & meets.tfrrs]
        .drop(columns=["date_begin", "meetpro", "sport", "outdoors", "url", "tfrrs"])
        .set_index("meet_hnd", drop=True)
    )

    return meets


def get_teams_leagues() -> tuple[pd.DataFrame, pd.DataFrame]:
    url = "https://www.tfrrs.org/js/navbar_autocomplete.js"

    with requests.get(url) as r:
        javascript = r.text

    dfs = []
    for table_name in ["autocomplete_teams", "autocomplete_conferences"]:
        # find meet array in retrieved javascript file
        pattern = rf"{table_name}\s*=\s*(\[(.|\n)+?\]);"
        json = re.search(pattern, javascript).group(1)
        json = json.replace("{text:", '{"text":').replace(",url:", ',"url":')

        df = pd.read_json(StringIO(json))  # load into dataframe

        # clean up
        df["name"] = df.text.str.replace(" (F)", "", regex=False).str.replace(
            " (M)", "", regex=False
        )

        df["id"] = (
            df.url.str.replace("/teams/", "", regex=False)
            .str.replace("/leagues/", "", regex=False)
            .str.replace("xc/", "", regex=False)
            .str.replace(".html", "", regex=False)
        )

        if "teams" in table_name:
            df["gender"] = ["M" if " (M)" in text else "F" for text in df.text]
            df["state"] = [id[:2] for id in df.id]

        df.set_index("id", inplace=True, drop=True)

        dfs.append(df.drop(columns=["url", "text"]).drop_duplicates())

    return tuple(dfs)


if __name__ == "__main__":
    get_meets().to_csv(OUTPUT_FOLDER / "meets.csv")
    # teams, leagues = get_teams_leagues()
    # teams.to_csv(OUTPUT_FOLDER / "teams.csv")
    # leagues.to_csv(OUTPUT_FOLDER / "leagues.csv")
