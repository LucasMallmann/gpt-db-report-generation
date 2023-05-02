import mysql.connector

# Hardcoded values for now
host = "database",
user = "root",
password = "dbreport",
database = "dbreport_test"


class MySQLConnection:
    __instance = None

    @staticmethod
    def get_instance():
        if MySQLConnection.__instance == None:
            MySQLConnection()
        return MySQLConnection.__instance

    def __init__(self) -> None:
        if MySQLConnection.__instance != None:
            raise Exception(
                "You cannot instantiate more than one MySQLConnection")
        else:
            MySQLConnection.__instance = self
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                passwd=password,
                database=database
            )

    def execute_query(self, query: str, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
