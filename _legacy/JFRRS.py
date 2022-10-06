import os
from pathlib import Path
import sqlite3
from typing import Iterable

import pandas as pd


import scraper

"""
TODO:
 - add consistent docstring format
 - write tests
 - profile to see if multithreading/async scraping is worthwhile
"""

#############
# CONSTANTS #
#############

DB_SCHEMA_PATH = Path("tables")


####################
# MAIN JFRRS CLASS #
####################


class JFRRS:
    _db: sqlite3.Connection

    noisy: bool = True

    ################
    # CONSTRUCTION #
    ################

    def __init__(self, db_path="jfrrs.db"):
        """ "
        Creates a new JFRRS instance from the provided database.
        """
        new_db = not os.path.exists(db_path)

        self._db = sqlite3.connect(db_path)

        if new_db:
            self._create_tables()

    def _create_tables(self):
        """
        Creates tables for database using commands in the
        `DB_SCHEMA_PATH` folder (`/schema` by default).
        """
        tables = ["meets.txt", "teams.txt", "athletes.txt", "results.txt"]
        for table_file in tables:
            with open(DB_SCHEMA_PATH / table_file, "rt", encoding="utf8") as f:
                self._db.execute(f.read())

    ##################
    # SCRAPING MEETS #
    ##################

    def add_recent_meets(self, n_meets=100) -> list[int]:
        """
        TODO: docstring
        """
        meets = scraper.recent_meets()
        failed = []
        succeeded = []

        while len(succeeded) < n_meets:
            _, meet_id = next(meets, None)

            if not meet_id:
                if self.noisy:
                    print("No more available meets.")
                break

            if self._contains("meets", meet_id):
                if self.noisy:
                    print(" - Meet already scraped")
                continue

            try:
                self.add_meet(meet_id)
                succeeded.append(meet_id)

            except Exception as e:  # pylint: disable=broad-except
                if self.noisy:
                    print(f"Unable to scrape {meet_id}.")
                    print(" - ", end="")
                    print(e)
                failed.append(meet_id)

        if self.noisy:
            print(f"\nSuccessfully scraped {len(succeeded)} meets.")
            print(f"Failed on {', '.join(map(str, failed))}")

        return succeeded

    def add_meet(self, meet_id: int) -> bool:
        """
        TODO: docstring
        """
        if self.noisy:
            print(f"\nScraping meet {meet_id} ...")

        if self._contains("meets", meet_id):
            print(" - Already scraped")
            return False

        # process meet information
        meet_info, results = scraper.scrape_meet(meet_id)

        if self.noisy:
            print(f" - {meet_info['name']}")
            print(f" - {meet_info['date']}")
            print(f" - {meet_info['distance']}")
            print(f" - {meet_info['venue']} ({meet_info['location']})")

        try:
            self._insert("meets", (
                meet_info["id"],
                meet_info["name"],
                meet_info["date"],      # TODO: define format
                meet_info["distance"],  # in meters
                meet_info["venue"],     # e.g., Carleton College
                meet_info["location"],  # e.g., Northfield, MN
            ))  # fmt: skip
        except sqlite3.IntegrityError as e:
            if self.noisy:
                print(f" - Failed scraping {meet_info['name']} ({meet_id}).") 
                print(f" - {e}")
            return False

        # process results, adding entries for new athletes and teams as they are encountered
        n_scraped = 0
        for result in results:

            if not self._contains("athletes", result["athlete_id"]):
                self._insert(
                    "athletes",
                    (
                        result["athlete_id"],
                        result["athlete_firstname"],
                        result["athlete_lastname"],
                        result["team_id"],
                    ),
                )

            if not self._contains("teams", result["team_id"]):
                self._insert(
                    "teams",
                    (result["team_id"], result["team_name"]),
                )

            self._insert(
                "results",
                (None, result["athlete_id"], meet_id, result["time"], result["score"]),
            )

            n_scraped += 1

        if self.noisy:
            print(f" - Successfully scraped {n_scraped} results.")

        self._db.commit()
        return True

    ###########################
    # DATABASE HELPER METHODS #
    ###########################

    # possible sql injection below, but these are internal methods
    # and this isn't production code so ... not worth fixing

    def _contains(self, table_name: str, id_: int | str) -> bool:
        if id_ is None:  # in the case of DNF, unattached athlete w/o id, etc.
            return True

        query = f"SELECT * FROM {table_name} WHERE id == '{id_}'"
        return self._db.execute(query).fetchone() is not None

    def _insert(self, table_name: str, row: tuple) -> None:
        """
        General internal helper method to add rows to a table in the database.
        """
        placeholder = "(" + ",".join(["?"] * len(row)) + ")"
        self._db.execute(f"INSERT INTO {table_name} VALUES {placeholder}", row)

    ###################
    # MEET PREDICTION #
    ###################

    def predict_meet(self, team_ids: Iterable[str | int]) -> pd.DataFrame:
        # pylint: disable=unused-variable

        # protect against injection
        if not all(isinstance(team_id, int | str) for team_id in team_ids):
            raise ValueError(f"team_ids must be a list of ints. Passed {team_ids=}.")

        athlete_ids = self._db.execute(
            f"SELECT id FROM athletes WHERE team_id IN {', '.join(map(str, team_ids))}"
        )

        # TODO: implement
        raise NotImplementedError()

    #######################
    # I/O AND CONVENIENCE #
    #######################

    def export_tables(self, folder: os.PathLike = None) -> None:
        """
        Export the database to csv if `folder` is provided.
        Print first 30 rows to stdout otherwise.
        """
        folder = Path(folder)

        tables = ["meets", "teams", "athletes", "results"]
        for table in tables:
            df = pd.read_sql(f"SELECT * FROM {table};", self._db)
            if folder:
                df.to_csv(folder / f"{table}.csv", index=False)
            else:
                print(df.head(30))

    def get_meet_results(self, meet_id):

        query = """
        SELECT 
            athletes.first_name || " " || athletes.last_name name,
            teams.name team,
            results.time,
            results.score
        FROM
            results
            JOIN athletes ON results.athlete_id = athletes.id
            JOIN meets    ON results.meet_id    = meets.id
            JOIN teams    ON athletes.team_id   = teams.id
        WHERE
            meets.id == ?
        """

        df = pd.read_sql(query, self._db, params=(meet_id,))
        df = df.sort_values("time", ascending=True)

        if self.noisy:
            print(df.head(20))
            print(df.tail(20))

        return df


###########################
# TESTING AND DRIVER CODE #
###########################


def test():
    jfrrs = JFRRS(":memory:")

    jfrrs.add_meet(18785)
    # jfrrs.add_recent_meets(3)
    jfrrs.export_tables(folder="export")

    df = jfrrs.get_meet_results(18785)
    print(df.head(20))


def main():
    jfrrs = JFRRS("jfrrs.db")
    df = pd.read_csv("prescraping/meets.csv", index_col=0)
    meet_ids = reversed(df.index.to_list())

    for id in meet_ids:
        try:
            jfrrs.add_meet(id)
        except Exception as e:
            print(f" - failed. {e}")


    jfrrs.add_recent_meets()
    jfrrs.export_tables(folder="export")


if __name__ == "__main__":
    # test()
    # main()
    JFRRS("jfrrs.db").export_tables("export")
