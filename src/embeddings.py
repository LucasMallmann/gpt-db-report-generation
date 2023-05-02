import openai
import os
import sys
import mysql.connector
from mysql.connector import Error
import numpy as np
import modules.database as db

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to the MySQL database


def create_connection(host, user, password, database):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=database
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

# Fetch all comments from the table


def fetch_columns(db: db.MySQLConnection):
    query = """
SELECT
    t.TABLE_NAME AS table_name,
    c.COLUMN_NAME AS column_name,
    c.COLUMN_COMMENT AS comment
FROM 
    INFORMATION_SCHEMA.TABLES t 

INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
        ON t.TABLE_NAME = c.TABLE_NAME 
            AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
WHERE
    c.COLUMN_COMMENT <> ''
    AND t.TABLE_SCHEMA = 'dbreport_test' 
    AND t.TABLE_NAME = 'users';"""
    columns = db.execute_query(query)
    return columns


# Add embedings to embedding table
def insert_embedding(db: db.MySQLConnection, table_name, column_name, embedding):
    query = """
      INSERT INTO embeddings (
        table_name, column_name, embedding, 
        created_at, updated_at, deleted_at) 
        VALUES (%s, %s, %s, NOW(), NOW(), NULL)
    """
    db.execute_query(query, (table_name, column_name, str(embedding.tolist())))

# Generate embeddings using the text-embedding-ada-002 model


def generate_embedding(prompt):
    try:
        response = openai.Embedding.create(
            input=prompt,
            model="text-embedding-ada-002"
        )
        return np.array(response.data[0].embedding)
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


# Main script
if __name__ == "__main__":
    db = db.MySQLConnection.get_instance()

    if not db:
        sys.exit()

    columns = fetch_columns(db=db)
    for column in columns:
        table_name, column_name, comment = column
        embedding = generate_embedding(comment)

        print('Embedding generated: ', embedding)

        insert_embedding(db, table_name, column_name, embedding)
        print(
            f"Just addded embedding for table {table_name} column {column_name}")

    # Close the connection
    db.close_connection()
