import os
import openai
from dotenv import load_dotenv

# Read .env file
load_dotenv()
OPENAI_ENGINE = os.getenv('OPENAI_ENGINE') or 'text-davinci-003'
TEMPLATE_DIR = os.path.abspath('./tpl')
PROMPT_DIR = os.path.abspath('./prompts')
APP_PORT = os.getenv('APP_PORT') or 5000
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASS = os.getenv('DATABASE_PASS')
DATABASE_DB = os.getenv('DATABASE_DB')
DEBUG_MODE = (os.getenv('DEBUG_MODE').lower() == 'true') or False
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')

SQL_DATABASE_URI = f'mysql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}'

if OPENAI_TOKEN:
    openai.api_key = OPENAI_TOKEN
    os.environ['OPENAI_API_KEY'] = OPENAI_TOKEN
else:
    print('Please set OPENAI_TOKEN in .env file or set token in UI')
