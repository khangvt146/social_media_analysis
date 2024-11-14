import copy
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import sqlalchemy as sqla
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

USERNAME = ""
PASSWORD = ""
HOST = ""
PORT = "5432"
DATABASE = ""
SCHEMA = "public"


class PostgreConnector:
    """
    Modules that provides functionality to interact with PostgreSQL.
    """

    def __init__(self) -> None:
        super().__init__()

    def init_sql(self) -> None:
        """
        Initialize the PostgreSQL connector engine.

        Parameters:
            - config (dict): A dictionary containing configuration settings such as
                USERNAME, PASSWORD, HOST, PORT, etc.
        """
        self.engine_path = (
            f"postgresql://{USERNAME}:{quote_plus(PASSWORD)}@{HOST}:{PORT}/{DATABASE}"
        )

        if SCHEMA:
            self.engine = sqla.create_engine(
                self.engine_path,
                connect_args={"options": "-csearch_path={}".format(SCHEMA)},
            )
        else:
            self.engine = sqla.create_engine(self.engine_path)

    def execute_sql_command(self, sql: str) -> None:
        """
        Execute provided SQL command.

        Parameters:
            sql (str): The SQL command to execute.
        """
        with Session(self.engine) as session, session.begin():
            session.execute(text(sql))

    def insert_to_table(
        self, table_name: str, df: pd.DataFrame, schema: str = None
    ) -> None:
        """
        Insert a provided Pandas DataFrame into the specified table in the database.

        Parameters:
            - table_name (str): The name of the table in the database.
            - df (DataFrame): The DataFrame to be inserted into the database.
            - schema (str): The name of the schema where the table created in the database
        """
        if not df.empty:
            data = copy.deepcopy(df)
            table_name = table_name.lower()
            data.columns = data.columns.str.lower()
            data.to_sql(
                table_name,
                self.engine,
                if_exists="append",
                index=False,
                chunksize=10000,
                schema=schema,
            )

    def query_with_sql_command(self, sql: str) -> pd.DataFrame:
        """
        Query data from the database with provided SQL command.

        Parameters:
            sql (str): The SQL command to execute.

        Returns:
            pd.DataFrame: The resulting query DataFrame
        """
        result = pd.read_sql_query(text(sql), self.engine)
        result.columns = map(str.upper, result.columns)
        return result

    def execute_sql_command(self, sql: str) -> None:
        """
        Execute provided SQL command.

        Parameters:
            sql (str): The SQL command to execute.
        """
        with Session(self.engine) as session, session.begin():
            session.execute(text(sql))

    def query_with_in_list_condition(
        self, table_name: str, *column, **args
    ) -> pd.DataFrame:
        """
        Query data from the database with provided list of equal query condition.

        Parameters:
            - table_name (str): The table name in the database.
            - column (list): The column names to retrieve data from.
            - args (dict): The query conditions

        Returns:
            pd.DataFrame: The resulting query DataFrame

        Example: Query data from column "A" and "B" of the table name "TEST TABLE" with conditions that
            the values in column "A" is 10 and 20.
            ------------------------------------------------------------------
            sql.query_with_in_list_condition("TEST TABLE", ["A", "B"], A = [10, 20])
            ------------------------------------------------------------------
        """
        table_name = table_name.lower()

        # The column names parser
        if len(column) == 0:
            col_sql = "*"
        else:
            col_sql = ", ".join(column)

        # The condition parser
        if len(args) == 0:
            condition_query = ""
        else:
            condition_query = "where "

            condition_list = []
            for key, value in args.items():
                if isinstance(value, list):
                    condition_list.append(
                        f"{key} in "
                        + "('"
                        + "', '".join(np.array(value, dtype=str))
                        + "')"
                    )
                else:
                    condition_list.append(f"{key} = {value}")
            condition_query += " and ".join(condition_list)

        sql = f"select {col_sql} " f"from {table_name} " f"{condition_query}"

        result = pd.read_sql_query(text(sql), self.engine)
        result.columns = map(str.upper, result.columns)
        return result


if __name__ == "__main__":
    sql = PostgreConnector()
    sql.init_sql()

    # Query all columns in table "silver_reddit"
    # Approach 1
    reddit_df = sql.query_with_in_list_condition("silver_reddit")

    # Approach 2
    sql_cmd = "select * from silver_reddit"
    reddit_df = sql.query_with_sql_command(sql_cmd)

    # Insert DataFrame df to table "topic_clustering_1m"
    df = pd.DataFrame()
    sql.insert_to_table("topic_clustering_1m", df)

    # Delete all records in table "topic_clustering_1m"
    sql_cmd = "delete from topic_clustering_1m"
    sql.execute_sql_command(sql_cmd)
