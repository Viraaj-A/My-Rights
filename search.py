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
    search_term = search['searched']
    start_date = search['start_date']
    end_date = search['end_date']
    importance = search['importance']
    respondent = search['respondent']


    corrected = (spell(search_term))
    if corrected == search_term:
        search_term = search_term
    else:
        search_term = corrected
    sql_query = """
    SELECT item_id, url, case_title, importance_number, judgment_date, ts_headline('english', entire_text, query, 'StartSel = <b>, StopSel = </b>, ShortWord = 3, MinWords = 50, MaxWords = 60') as entire_text_highlights
    FROM (SELECT item_id, url, entire_text, case_title, importance_number, judgment_date, ts_rank_cd(textsearchable_index_col, query) AS rank, query
    FROM english_search, websearch_to_tsquery('english', %s) AS query
    WHERE textsearchable_index_col @@ query
    ORDER BY rank DESC
    LIMIT 10) AS query_results;
        """
    sql_tuple = (search_term,)
    cursor.execute(sql_query, sql_tuple)
    # The result structure is a list of tuples
    results = [cursor.fetchall()]
    return results




cursor, conn = connect_psql()
spell = Speller()

