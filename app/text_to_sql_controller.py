from flask import Blueprint

from llama_index import GPTSQLStructStoreIndex, SQLDatabase

from app.db import Database
import app.config as config

text_to_sql_bp = Blueprint('text_to_sql', __name__)

db = Database(config.SQL_DATABASE_URI)


@text_to_sql_bp.route('/llamaindex')
def index():
    query = "SELECT * FROM users"
    rows = db.execute_query(query)
    table_names = db.get_tables()
    sql_database = SQLDatabase(db.engine, include_tables=table_names)
    print('QUERY {} are {}'.format(query, rows))

    index = GPTSQLStructStoreIndex(sql_database=sql_database)
    query_engine = index.as_query_engine()
    response = query_engine.query(
        "Give me the email of a user called John Doe")

    print('Reponse is ', response)
    print('Extra info: ', response.extra_info['sql_query'])

    return {
        'success': True
    }
