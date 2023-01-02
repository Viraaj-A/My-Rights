from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

development = False


#Connecting with psycopg2/SQLAlchemy
if development == True:
    connection_string = 'postgres:password@localhost/restore_Oct_13'
else:
    connection_string = 'doadmin:AVNS_SbC_UqXYG665R47kxY4@db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com:25060/defaultdb'

engine = create_engine(f'postgresql+psycopg2://{connection_string}',poolclass=NullPool)
print('connected')

def pagination(search: str):
    select_statement ="""
            SELECT item_id, url, case_title, importance_number, judgment_date, facts, conclusion, ts_headline('english', entire_text, query, 'StartSel = <b>, StopSel = </b>, ShortWord = 3, MinWords = 50, MaxWords = 60') as entire_text_highlights
            FROM (SELECT item_id, url, entire_text, case_title, importance_number, judgment_date, facts, conclusion, ts_rank_cd(textsearchable_index_col, query) AS rank, query
            FROM english_search, websearch_to_tsquery('english', %s) AS query
            WHERE textsearchable_index_col @@ query
            ORDER BY rank DESC
            LIMIT 10) AS query_results;
            """

