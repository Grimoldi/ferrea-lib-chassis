"""
Small script in case of using Neo4J Aura to keep it alive.
A single node (Keepalive) is created/updated.
"""

import os
import sys
from datetime import datetime
from typing import Any, LiteralString

sys.path.append("./src/")  # quick and dirty
from ferrea.clients.db import ConnectionSettings, Neo4jClient

query = LiteralString
params = dict[str, Any]


def _client_factory() -> Neo4jClient:
    """Creates a Neo4jClient."""

    return Neo4jClient(
        connection_settings=ConnectionSettings(
            uri=os.environ["DB_URI"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PWD"],
            database=os.environ.get("DB_DB", "neo4j"),
        )
    )


def _query_builder() -> tuple[query, params]:
    """Build the query and parameters to use."""
    query = """//cypher
        MERGE (k: Keepalive)
        ON CREATE
          SET k.day = $day
        ON MATCH
          SET k.day = $day
        RETURN k
    """
    params = {"day": datetime.now().isoformat(timespec="seconds")}

    return query, params


def main() -> None:
    try:
        client = _client_factory()
        with client as session:
            [result] = session.write(*_query_builder())
            if result is None:
                print("::error::Unable to create/update the Keepalive node!")
                sys.exit(1)
            print("::notice::Successfully created/updated the Keepalive node.")
    except KeyError as e:
        print(f"::error::Unable to find os env {e}.")
        exit(1)
    except Exception:
        ex_type, ex_value, _ = sys.exc_info()
        print(
            f"::error::Unable to connect to db due to {ex_type.__name__}: {ex_value}."  # type: ignore
        )
        exit(1)


if __name__ == "__main__":
    main()
