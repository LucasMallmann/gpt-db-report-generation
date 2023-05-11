from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self, url: str):
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def get_tables(self):
        return list(self.metadata.tables.keys())

    def get_columns(self, tabl_name: str):
        inspector = inspect(self.engine)
        columns = inspector.get_columns(tabl_name)
        return [column['name'] for column in columns]

    def execute_query(self, query: str):
        with self.Session() as session:
            result = session.execute(text(query))
            rows = result.fetchall()
        return rows
