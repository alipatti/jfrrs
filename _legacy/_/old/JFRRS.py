import os
from datetime import datetime
import sqlite3 as sql
from operator import itemgetter
from itertools import chain, combinations, compress
from math import exp, log
from pickle import dump, load
from copy import copy
from typing import Iterable

import igraph as ig

from database import create_connection, create_tables
from scraper import recent_meets, scrape_meet


class JFRRS:
    """
    TFRRS scraper and XC meet predictor.
    """

    ##########################
    # I/O & CREATION METHODS #
    ##########################

    def save(self, filepath, overwrite=False) -> None:
        if os.path.exists(filepath) and not overwrite:
            raise FileExistsError(f"File {filepath} already exists.")

        # workaround for unpicklability of connection object
        obj = copy(self)
        del obj.cxn

        with open(filepath, "wb") as f:
            dump(obj, f)

        del obj

    @classmethod
    def load(cls, filepath):
        with open(filepath, "rb") as f:
            obj = load(f)

        # recreate database connection
        obj.cxn = create_connection(obj.database_path)

        return obj

    def __init__(
        self,
        database_path: str,
        graph_path: str = None,
        k: float = 2e-2,
    ):
        """
        Creates or loads an instance of JFRRS.
        If `graph_path` is not specified, it is assumed to be the
        same as `database_path` with a .graph.pkl file extension.
        """

        if not graph_path:
            graph_path = database_path.rsplit(".", 1)[0] + ".graph.pkl"

        new_database = not os.path.exists(database_path)

        self.database_path = database_path
        self.cxn = create_connection(database_path)

        if new_database:
            print(f"Creating new database at {database_path}")
            create_tables(self.cxn)

        self.meets = self.get_all_ids("meets")
        self.teams = self.get_all_ids("teams")
        self.athletes = self.get_all_ids("athletes")

        self.k = k

        if os.path.exists(graph_path):
            self.graph: ig.Graph = ig.load(graph_path)
            self.update_graph()
        else:
            self.graph = self.create_graph()

        self.last_update = datetime.today()

    ####################################
    # SCRAPING AND DATABASE MANAGEMENT #
    ####################################

    def get_all_ids(self, table: str) -> set:
        return set(id for id, in self.cxn.execute(f"SELECT TFRRS_id FROM {table}"))

    def _add(self, table: str, values, commit=False):
        """
        General method to add values to a table in the database.
        Values is either a tuple or a list of tuples of the same size
        as a row in the specified table.
        """
        if isinstance(values, tuple):
            values = [values]

        values = map(str, values)

        try:
            for row in values:
                self.cxn.execute(f"INSERT INTO {table} VALUES {str(row)}")
            if commit:
                self.cxn.commit()
        except sql.Error as err:
            print(f"Unable to add {row} to {table}. SQLite error: {err}")

    def add_meet(self, meet_id: int):
        """
        Adds meet and all its times to provided SQLite database, adding
        teams and athletes as needed. Does nothing if meet is already
        in database.
        """
        if meet_id in self.meets:
            print(f"Meet already in database: {meet_id}.")
            return None

        info, results = scrape_meet(meet_id)
        athletes, teams = [], []

        if not results:
            print(f"Unable to scrape meet: {info[1]}")
            return False

        self._add("meets", list(info.items()))

        results = filter(all, results)  # remove unattached runners, DNFs, etc.

        # for athlete_name, athlete_id, team_name, team_id, time in results:
        #     if athlete_id not in self.athletes:
        #         self._add("athletes", (athlete_id, athlete_name, team_id))
        #         athletes.append(athlete_id)

        #     if team_id not in self.teams:
        #         self._add("teams", (team_name, team_id))
        #         teams.append(team_id)

        #     self._add("performances", (athlete_id, meet_id, time))

        for entry in results:
            entry["time"]

        self.cxn.commit()
        # don't update sets until entries are committed to database
        self.meets.add(meet_id)
        self.athletes.update(athletes)
        self.teams.update(teams)
        print(f"Successfully scraped meet: {info[1]}.")
        return True

    def add_recent_meets(self, n: int = 10):
        """
        Adds recent meets from TFRRS. Stops when `n` meets have been scraped.
        """
        meets = recent_meets()

        n_scraped = 0
        while n_scraped < n:
            _, meet_id = next(meets, None)

            if not meet_id: 
                print("All available meets have been scraped.")
                break

            self.add_meet(meet_id)
            n_scraped += 1
            
        print("Successfully scraped {i} meets.")

    ###################
    # MEET PREDICTION #
    ###################

    def get_edges(
        self,
        meet_ids: list[str] = None,
    ) -> list[tuple[int, int, float, int]]:
        """Finds all head to head edges between given meets and
        returns edges in format `(source, dest, weight, meet_id)`.
        If `meet_ids` is not specified, all meets are processed."""

        query = """
            SELECT TFRRS_id, date
            FROM meets
            """

        if meet_ids:
            query += f"""
                WHERE meet_id
                IN {'?, ' * len(meet_ids-1)}?"""

        edges = []
        query_results = (
            self.cxn.execute(query, meet_ids) if meet_ids else self.cxn.execute(query)
        )

        for meet_id, date in query_results:
            query = f"""
                SELECT athlete_id, time
                FROM performances
                WHERE meet_id == {meet_id}
                """
            results = sorted(self.cxn.execute(query), key=itemgetter(-1))
            edges.extend(
                (int(id_u), int(id_v), _weight(t_v - t_u, date), int(meet_id))
                for (id_u, t_u), (id_v, t_v) in combinations(results, 2)
            )

        return edges

    def update_graph(self):
        """Updates the head-to-head graph:

        Diminishes weight of existing edges according to determined
        exponential decay function; updates from results in the
        database not yet in the graph."""

        # decay existing edges
        decay = lambda w, t: w * exp(-self.k * t)
        time_passed = (datetime.today() - self.last_update).days

        old_weights = self.graph.es["weight"]
        new_weights = [decay(w, time_passed) for w in old_weights]
        self.graph.es["weight"] = new_weights

        meets_in_graph = set(self.graph.es["meet_id"])
        athletes_in_graph = set(self.graph.es[""])
        meets_to_add = self.meets - meets_in_graph
        athletes_to_add = self.athletes - athletes_in_graph

        self.graph.add_vertices(athletes_to_add)

        # TODO add new edges
        self.get_edges()

    def create_graph(self) -> ig.Graph:
        """Creates head-to-head performance graph with (u, v) in E
        if u beat v at some meet. Edge weight is determined by
        meet recency and difference in finishing time."""

        edges = self.get_edges()

        graph = ig.Graph.TupleList(
            edges,
            directed=True,
            vertex_name_attr="id",
            edge_attrs=["weight", "meet_id"],
        )

        return graph

    def subgraph_topo_order(
        self,
        athlete_ids: list[int],
        exact=True,
        graph=None,
        simplify=True,
    ) -> list[int]:
        """Gets topological order of MAS of induced subgraph containing
        `vertices`."""

        graph = graph if graph else self.graph

        subgraph = self.subgraph(athlete_ids, simple=simplify)

        naughty_edges = subgraph.feedback_arc_set(
            weights="weight", method=("ip" if exact else "eades")
        )

        subgraph.delete_edges(naughty_edges)

        return subgraph[subgraph.topological_sorting()]["id"]

    def get_top_seven(self, team_id: str) -> list[int]:
        """Gets team's top seven runners via topological sort of
        team's MAS."""
        query = """
            SELECT TFRRS_id
            FROM athletes
            WHERE team_id == ?
            """

        # TODO handle situation where graph isn't connected

        runners = [row[0] for row in self.cxn.execute(query, (team_id,))]

        return self.subgraph_topo_order(runners)[:7]

    def subgraph(self, athlete_ids: Iterable[int], simple=False) -> ig.Graph:
        """Creates simple subgraph with given athlete ids. Combines
        parallel and mutual edges into a single edge."""

        graph_indices = self.graph.vs(id_in=set(athlete_ids))
        subgraph = self.graph.induced_subgraph(graph_indices)

        if not simple:
            return subgraph

        # remove parallel edges
        subgraph = subgraph.simplify(combine_edges=sum)

        # remove mutual edges
        # (there's probably a more elegant way to do this)
        to_delete = []
        new_weights = subgraph.es["weight"]
        for e in compress(subgraph.es, subgraph.is_mutual()):
            uv = subgraph.get_eid(*e.tuple)
            vu = subgraph.get_eid(*reversed(e.tuple))
            weight_dif = new_weights[uv] - new_weights[vu]
            if weight_dif > 0:
                new_weights[uv] = weight_dif
                to_delete.append(vu)

        subgraph.es["weights"] = new_weights
        subgraph.delete_edges(to_delete)

        return subgraph

    def get_affiliated_athletes(
        self,
        athletes: list[int],
        # n: int=None
    ) -> set[int]:
        """Returns a list of athlete ids which are part of the
        in-neighborhood and the out-neighborhood of the
        subset of `V` given by `athletes`."""
        # TODO return the n most-raced-against athletes (use a Counter)
        # or those with the most flow across the boundary of athletes
        out_neighbors = set(
            chain.from_iterable(self.graph.neighborhood(athletes, order=1, mode="out"))
        )
        in_neighbors = set(
            chain.from_iterable(self.graph.neighborhood(athletes, order=1, mode="in"))
        )

        return in_neighbors & out_neighbors

    def predict_meet(
        self, team_ids: list[str], exact: bool = True, include_affiliated: bool = False
    ) -> list[int]:
        """
        Predicts XC meet by finding the 'best' order over the athletes
        such the fewest "important" head-to-head performances are violated,
        where importance is determined by a weight function which takes into
        account the difference in finishing time and how long ago the
        meet was.

        Setting `include_affiliated` to True causes the algorithm to
        consider athletes who have both raced against multiple people
        in the meet and been beaten someone in the simulated meet.

        Returns a list of athlete's TFRRS_ids ordered from best to worst.
        """

        teams = dict(
            zip(team_ids, [self.get_top_seven(team_id for team_id in team_ids)])
        )
        athletes = list(chain(*teams.values()))

        if include_affiliated:
            affiliated = self.get_affiliated_athletes(athletes)
            athletes.extend(affiliated)

        ranking = self.subgraph_topo_order(athletes)

        indiv_results = (
            ranking
            if not include_affiliated
            else [a for a in ranking if a not in affiliated]
        )

        # TODO calculate team results
        team_results = []

        return indiv_results, team_results


def _weight(time_difference: float, date: str) -> float:
    # TODO add other contributors to the weight
    # importance of meet
    # standard dev from athlete's normal performance

    k = -log(0.5) / 30  # gives half-life of 30 days
    t_since_meet = datetime.today() - datetime.strptime(date, "%m/%d/%Y")
    return time_difference * exp(k * t_since_meet.days)
