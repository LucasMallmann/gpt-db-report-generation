import os
import json
import time
import openai
import mysql.connector
from mysql.connector import Error
from flask import Blueprint, render_template, request

import app.config as config
from schema import Schema


main_blueprint = Blueprint(
    'main', __name__, template_folder=config.TEMPLATE_DIR)

# Generate SQL Schema from MySQL
schema = Schema()
sql_schema, json_data = schema.index()
print('SQL data was generated successfully.')


def load_prompt(name: str) -> str:
    """Load prompt from file"""
    with open(os.path.join(config.PROMPT_DIR, name + ".txt"), 'r', encoding='utf-8') as file:
        return file.read()


@main_blueprint.route('/')
def index():
    """Show SQL Schema + prompt to ask GPT-3 to generate SQL queries"""
    normalized_json_data = json.dumps(json_data)
    return render_template(
        'index.html',
        has_openai_key=bool(openai.api_key),
        sql_schema=sql_schema,
        json_data=normalized_json_data
    )


@main_blueprint.before_request
def get_key():
    """Get API key from request or .env file"""
    if (request.content_type != 'application/json'
        or request.method != 'POST'
            or request.path == '/run'):
        return
    content = request.json
    if not content['api_key'] and not openai.api_key:
        return {
            'success': False,
            'error': 'Please set OPENAI_TOKEN in .env file or set token in UI'
        }

    if content and content['api_key']:
        request.api_key = content['api_key']
    else:
        request.api_key = config.OPENAI_TOKEN


@main_blueprint.post('/generate')
def generate():
    """Generate SQL query from prompt + user input"""
    try:
        content = request.json
        user_input = content['query']
        query_temperture = content['temp']
        selected = content['selected']
        print('Selected tables:', selected)
        print('User input:', user_input)
        print('Query temperture:', query_temperture)

        openai.api_key = request.api_key
        regen_schema = schema.regen(selected)
        fprompt = load_prompt('sql').replace(
            '{regen_schema}', regen_schema).replace('{user_input}', user_input)
        # Edit prompt on the fly by editing prompts/sql.txt
        print(f'Final prompt: {fprompt}')

        # Ask GPT-3
        gpt_response = openai.Completion.create(
            engine=config.OPENAI_ENGINE,
            prompt=fprompt,
            temperature=float(query_temperture),
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"]
        )

        used_tokens = gpt_response['usage']['total_tokens']

        # Get SQL query
        sql_query = gpt_response['choices'][0]['text']
        sql_query = sql_query.lstrip().rstrip()
        print('Generated SQL query:', sql_query)

        # Return json
        return {
            'success': True,
            'sql_query': sql_query,
            'used_tokens': used_tokens,
        }
    except Exception as err:
        print(err)
        return {
            'success': False,
            'error': str(err)
        }


@main_blueprint.post('/run')
def execute():
    """Execute SQL query and show results in a table"""
    # Get SQL query
    try:
        ts_start = time.time()
        content = request.json
        sql_query = content['query']
        print('Run SQL query:', sql_query)

        # Execute SQL query and show results in a table
        conn = mysql.connector.connect(
            host=config.DATABASE_HOST,
            user=config.DATABASE_USER,
            passwd=config.DATABASE_PASS,
            database=config.DATABASE_DB
        )
        cur = conn.cursor()
        cur.execute(sql_query)
        results = cur.fetchall()

        # Return json with all columns names and results
        columns = [desc[0] for desc in cur.description]
        def transform(item): return item.decode() if type(
            item) is bytearray else item
        results = [map(transform, item) for item in results]
        results = [dict(zip(columns, row)) for row in results]
        seconds_elapsed = time.time() - ts_start
        return {
            'success': True,
            'columns': columns,
            'results': results,
            'seconds_elapsed': seconds_elapsed
        }
    except Error as err:
        print(err)
        return {
            'success': False,
            'error': str(err)
        }
    except Exception as err:
        print(err)
        return {
            'success': False,
            'error': str(err)
        }


@main_blueprint.post('/generate_prompt')
def generate_prompt():
    """Generate prompt from selected tables"""
    try:
        content = request.json
        selected = content['selected']
        query_temperture = content['temp']

        openai.api_key = request.api_key

        # Update prompt
        regen_schema = schema.regen(selected)
        final_prompt = load_prompt('idk').replace(
            '{regen_schema}', regen_schema)
        print(f'Final prompt: {final_prompt}')

        gpt_response = openai.Completion.create(
            engine=config.OPENAI_ENGINE,
            prompt=final_prompt,
            temperature=float(query_temperture),
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"]
        )

        used_tokens = gpt_response['usage']['total_tokens']

        # Get SQL query
        query = gpt_response['choices'][0]['text'].lstrip().rstrip()
        print('Generated prompt:', query)

        return {
            'success': True,
            'query': query,
            'used_tokens': used_tokens,
        }
    except Exception as err:
        print(err)
        return {
            'success': False,
            'error': str(err)
        }
