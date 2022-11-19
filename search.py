import psycopg2
from autocorrect import Speller

development = False

def connect_psql():
    if development == True:
        try:
            conn = psycopg2.connect(database="restore_Oct_13",
                                    host="localhost",
                                    user="postgres",
                                    password="password")
            print("connected")
        except:
            print("failed")
        cursor = conn.cursor()
        return cursor, conn

    if development == False:
        try:
            conn = psycopg2.connect(database="defaultdb",
                                    host="db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com",
                                    user="doadmin",
                                    password="AVNS_SbC_UqXYG665R47kxY4",
                                    port=25060,
                                    sslmode='require')
            print("connected")
        except:
            print("failed")
        cursor = conn.cursor()
        return cursor, conn


def text_search(search: str):
    corrected = (spell(search))
    if corrected == search:
        sql_query = """
        SELECT item_id, requests_url, ts_headline('english', entire_text, query, 'StartSel = <em>, StopSel = </em>, ShortWord = 1') as entire_text_highlights
        FROM (SELECT item_id, requests_url, entire_text, ts_rank_cd(textsearchable_index_col, query) AS rank, query
        FROM processed_judgment_html, websearch_to_tsquery('english', %s) AS query
        WHERE textsearchable_index_col @@ query
        ORDER BY rank DESC
        LIMIT 10) AS query_results;
            """
        sql_tuple = (search,)
        cursor.execute(sql_query, sql_tuple)
        # The result structure is a list of tuples
        results = [cursor.fetchall()]
        return results
    else:
        search = spell(search)
        sql_query = """
        SELECT item_id, requests_url, ts_headline('english', entire_text, query, 'StartSel = <em>, StopSel = </em>, ShortWord = 1') as entire_text_highlights
        FROM (SELECT item_id, requests_url, entire_text, ts_rank_cd(textsearchable_index_col, query) AS rank, query
        FROM processed_judgment_html, websearch_to_tsquery('english', %s) AS query
        WHERE textsearchable_index_col @@ query
        ORDER BY rank DESC
        LIMIT 10) AS query_results;
            """
        sql_tuple = (search,)
        cursor.execute(sql_query, sql_tuple)
        # The result structure is a list of tuples
        results = [cursor.fetchall()]
        return results


cursor, conn = connect_psql()
spell = Speller()