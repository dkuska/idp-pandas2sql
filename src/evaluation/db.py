from typing import NamedTuple

import psycopg2


class PostgresConfig(NamedTuple):
    host: str
    port: str
    database: str
    user: str
    password: str


POSTGRES_TPC_H_1GB_CONFIG = PostgresConfig(
    host="172.20.18.12", port="5777", database="tpc_h_1gb", user="admin", password="idp22-hisssql"
)

POSTGRES_TPC_H_10GB_CONFIG = PostgresConfig(
    host="172.20.18.12", port="5777", database="tpc_h_10gb", user="admin", password="idp22-hisssql"
)

LOCAL_CONFIG_01GB = PostgresConfig(
    host="localhost", port="5432", database="tpc_h_01gb", user="postgres", password="mypassword"
)

LOCAL_CONFIG_1GB = PostgresConfig(
    host="localhost", port="5432", database="tpc_h_1gb", user="postgres", password="mypassword"
)


class PostgresConnection:
    """
    Usage:
    `with PostgresConnection(POSTGRES_TPC_H_10GB_CONFIG) as conn:
        # do something with conn
    `
    This will automatically open and close the connection
    """

    def __init__(self, config: PostgresConfig):
        self.config = config

    def __enter__(self):
        self._conn = psycopg2.connect(**self.config._asdict())
        return self._conn

    def __exit__(self, *args, **kwargs):
        self._conn.close()
