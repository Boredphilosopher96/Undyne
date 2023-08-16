import os
from contextlib import contextmanager
from typing import Union, List

from dotenv import load_dotenv, find_dotenv
from flask import current_app
from psycopg2.extras import DictCursor
from psycopg2.pool import ThreadedConnectionPool

import utils

pool = None

load_dotenv(find_dotenv(utils.get_project_base_path()))


def setup():
    global pool
    DATABASE_URL = os.environ.get("DATABASE_URL")
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn = DATABASE_URL)


@contextmanager
def get_db_connection():
    try:
        connection = None
        while connection is None:
            try:
                connection = pool.getconn()
            except:
                current_app.logger.info("failed to get connection. retrying immediately.")
        
        yield connection
    finally:
        if connection is not None:
            pool.putconn(connection)


@contextmanager
def get_db_cursor(commit = False) -> DictCursor:
    """use commit = true to make lasing changes. Call this function in a with statement"""
    with get_db_connection() as connection:
        
        cursor = connection.cursor(cursor_factory = DictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()


def execute_query_from_files(file_paths: Union[str, List[str]], parameters, get_result = False):
    with get_db_cursor(commit = True) as cursor:
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        for file_path in file_paths:
            with open(file_path) as file:
                query = file.read()
                cursor.execute(query, parameters)
                if get_result:
                    res = cursor.fetchall()
        return res if get_result else None
