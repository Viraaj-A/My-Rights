import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

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
        # CONNECTION_STRING is "user:password@host:port/dbname" (see .env.example)
        conn = psycopg2.connect(f"postgresql://{os.environ['CONNECTION_STRING']}",
                                sslmode=os.getenv("DB_SSLMODE", "prefer"))
        cursor = conn.cursor()
        return cursor, conn


def exploded_articles(conn):
    sql_query = """
        SELECT * from ecli_articles
    """
    ecli_articles = pd.read_sql_query(sql_query, conn)
    return ecli_articles

cursor, conn = connect_psql()


def ecli_results(search_rights):
    """
    Reading a CSV file that associates the long form name of a right to just it's number
    The association allows the results of the questionnaire to be associated with the number.
    The exploded_articles function, brings in all the ecli_articles table, which is comprised of two columns, one
    that contains ECLI numbers, and the second that lists the articles' in that specific case.
    A dataframe is created to filter out any case that does not contain the relevant right.
    A groupby is created and sorted, to prioritise the cases that contain the highest number of relevant rights.
    PostgreSQL query is ran to return all the relevant cases.
    """
    cursor, conn = connect_psql()
    article_groups = pd.read_csv("data/answers_to_articles.csv")
    # Search_rights are the articles that apply to the user.
    filtered_df = article_groups[article_groups.full_name.isin(search_rights)]
    article_number_list = filtered_df.short_name.values.tolist()
    df = exploded_articles(conn)
    df_1 = df[df.unnest.isin(article_number_list)]
    ecli_results = df_1.groupby(['ecli']).size().to_frame('count').reset_index().sort_values('count', ascending=False)
    ecli_list = ecli_results['ecli'].to_list()
    return ecli_list, ecli_results




