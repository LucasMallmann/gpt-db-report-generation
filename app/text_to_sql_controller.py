from flask import Blueprint, render_template
from llama_index import GPTSQLStructStoreIndex, SQLDatabase
import json

from app.db import Database
import app.config as config

text_to_sql_bp = Blueprint(
    'text_to_sql', __name__, url_prefix='/llamaindex', template_folder=config.TEMPLATE_DIR)

db = Database(config.SQL_DATABASE_URI)

table_names = db.get_tables()
database_columns_config = [
    {table_name: db.get_columns(table_name)} for table_name in table_names]

sql_database = SQLDatabase(db.engine, include_tables=table_names)
index = GPTSQLStructStoreIndex(sql_database=sql_database)
query_engine = index.as_query_engine()


@text_to_sql_bp.route('/')
def index():
    return render_template(
        'llamaindex.html',
        database_tables=json.dumps(database_columns_config),
    )
