import os

from db import database_handler
from db.level.level_models import CommentData, LevelData

BASE_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/sql"


def get_level_info(level_id):
    return database_handler.execute_query_from_files(f"{BASE_PATH}/level_info.sql", (level_id,), get_result = True)


def get_comment_info(comment_id):
    return database_handler.execute_query_from_files(f"{BASE_PATH}/comment_info.sql", (comment_id,), get_result = True)


def get_level_comments(level_id):
    return database_handler.execute_query_from_files(f"{BASE_PATH}/level_comments.sql", (level_id,), get_result = True)


def add_level_comment(comment_data: CommentData):
    query_file_paths = [f"{BASE_PATH}/add_level_comment.sql", f"{BASE_PATH}/update_level_rating.sql"]
    database_handler.execute_query_from_files(query_file_paths, comment_data.model_dump())


def update_level_comment(comment_data: CommentData):
    query_file_paths = [f"{BASE_PATH}/update_level_comment.sql", f"{BASE_PATH}/update_level_rating.sql"]
    database_handler.execute_query_from_files(query_file_paths, comment_data.model_dump())


def delete_comment(comment_id, level_id):
    with database_handler.get_db_cursor(commit = True) as cursor:
        with open(f"{BASE_PATH}/delete_comment.sql") as file:
            query = file.read()
            cursor.execute(query, (comment_id,))
        with open(f"{BASE_PATH}/update_level_rating.sql") as file:
            query = file.read()
            cursor.execute(query, dict(level_id = level_id))


def update_level(level_data: LevelData):
    database_handler.execute_query_from_files(f"{BASE_PATH}/update_level.sql", level_data.dict())


def delete_level(level_id):
    database_handler.execute_query_from_files(f"{BASE_PATH}/delete_level.sql", (level_id,))


def add_level(level_data: LevelData):
    return database_handler.execute_query_from_files(
        f"{BASE_PATH}/add_level.sql",
        level_data.model_dump(),
        get_result = True
    )[0]
