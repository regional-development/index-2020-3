import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())
MSSQL = os.environ.get("MSSQL")
POSTGRESQL = os.environ.get("POSTGRESQL")


def db_connect(query, db="MSSQL"):
    """Зчитує таблицю з бази даних.


    Parameters
    ----------
    query : str
        sql query, напр. SELECT * FROM "Budget"."Incomes";
    """
    _db = MSSQL if db == "MSSQL" else POSTGRESQL
    con = create_engine(_db)
    return pd.read_sql(query, con)
