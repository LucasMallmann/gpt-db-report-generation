from flask import Blueprint, request, make_response, jsonify
from llama_index import GPTSQLStructStoreIndex, SQLDatabase

from app.db import Database
import app.config as config

text_to_sql_bp = Blueprint('text_to_sql', __name__, url_prefix='/llamaindex')

db = Database(config.SQL_DATABASE_URI)


def create_index():
    table_names = db.get_tables()
    sql_database = SQLDatabase(db.engine, include_tables=table_names)
    index = GPTSQLStructStoreIndex(sql_database=sql_database)
    return index.as_query_engine()


@text_to_sql_bp.route('/query', methods=['GET', ])
def index():
    global manager
    query_text = request.args.get("text", None)
    if query_text is None:
        return ("No text found, please include a ?text=blah parameter in the URL", 400)
    query_index = create_index()
    response = query_index.query(query_text)
    result = response.extra_info['result']

    if len(result) <= 0:
        return make_response(jsonify({"text": "No results found"})), 200

    transformed_result = [item._asdict() for item in result]

    response_json = {
        "sql_query": response.extra_info['sql_query'],
        "result": transformed_result,
    }
    return make_response(jsonify(response_json)), 200
