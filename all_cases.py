from sqlalchemy import text, create_engine
from sqlalchemy.pool import NullPool
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv('CONNECTION_STRING')

engine = create_engine(f'postgresql+psycopg2://{connection_string}',poolclass=NullPool)


class DF_All_Cases:
    query = text(""" Select
                    case_title,
                    ecli,
                    importance_number,
                    facts,
                    conclusion,
                    judgment_date,
                    url
                    From english_search;
                """)
    dataFrameHolder = pd.read_sql(query, engine.connect())