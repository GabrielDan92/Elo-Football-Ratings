import os

import psycopg2

from src.db.queries import (
    CREATE_PLAYED_GAMES_TABLE,
    CREATE_SCHEDULED_GAMES_TABLE,
    DROP_SCHEDULED_GAMES_TABLE,
)
from src.db.singleton import Singleton


class PostgreSQL(metaclass=Singleton):
    """
    A Singleton class representing a PostgreSQL database connection handler.

    This class manages a single database connection and provides methods for creating
    tables, performing batch inserts and executing queries on the connected database.
    """

    def __init__(self):
        self.conn = self.open_conn()
        self.create_games_tables()

    def create_games_tables(self):
        # create the required 'played_games' and 'scheduled_games' tables in the database
        with self.conn.cursor() as cur:
            cur.execute(DROP_SCHEDULED_GAMES_TABLE)
            cur.execute(CREATE_PLAYED_GAMES_TABLE)
            cur.execute(CREATE_SCHEDULED_GAMES_TABLE)

    def batch_insert(self, query, values):
        # execute a batch insert operation using the provided SQL query and values.
        with self.conn.cursor() as cur:
            cur.executemany(query, values)

    def query(self, query, values=None):
        # execute a query on the database and return the fetched results.
        with self.conn.cursor() as cur:
            cur.execute(query, values)

            return cur.fetchall()

    def open_conn(self):
        # establish a connection to the PostgreSQL database using environment variables
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USERNAME"),
            password=os.environ.get("DB_PASSWORD"),
            port=os.environ.get("DB_PORT"),
        )

        return conn

    def close_conn(self):
        # commit any pending transactions and close the database connection
        self.conn.commit()
        self.conn.close()
