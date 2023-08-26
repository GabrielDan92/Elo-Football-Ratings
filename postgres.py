import psycopg2
import os

from queries import CREATE_PLAYED_GAMES_TABLE, CREATE_SCHEDULED_GAMES_TABLE
from singleton import Singleton


class PostgreSQL(metaclass=Singleton):
    def __init__(self):
        self.conn = self.open_conn()
        self.create_games_tables()

    def create_games_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(CREATE_PLAYED_GAMES_TABLE)
            cur.execute(CREATE_SCHEDULED_GAMES_TABLE)

    def batch_insert(self, query, values):
        with self.conn.cursor() as cur:
            cur.executemany(query, values)

    def query(self, query, values=None):
        with self.conn.cursor() as cur:
            cur.execute(query, values)

            return cur.fetchall()

    def open_conn(self):
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USERNAME"),
            password=os.environ.get("DB_PASSWORD"),
            port=os.environ.get("DB_PORT")
        )

        return conn

    def close_conn(self):
        self.conn.commit()
        self.conn.close()
