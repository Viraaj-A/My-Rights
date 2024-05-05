from sqlalchemy import text, create_engine
from sqlalchemy.pool import NullPool
import pandas as pd

connection_string = 'doadmin:AVNS_SbC_UqXYG665R47kxY4@db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com:25060/defaultdb'

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