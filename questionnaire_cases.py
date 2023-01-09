import psycopg2
import pandas as pd

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
        conn = psycopg2.connect(database="defaultdb",
                                host="db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com",
                                user="doadmin",
                                password="AVNS_SbC_UqXYG665R47kxY4",
                                port=25060,
                                sslmode='require')
        cursor = conn.cursor()
        return cursor, conn


def exploded_articles():
    sql_query= """
        SELECT * from ecli_articles
    """
    ecli_articles = pd.read_sql_query(sql_query, conn)
    return ecli_articles

cursor, conn = connect_psql()

def test_results():
    """
    Reading a CSV file that associates the long form name of a right to just it's number
    The association allows the results of the questionnaire to be associated with the number.
    The exploded_articles function, brings in all the ecli_articles table, which is comprised of two columns, one
    that contains ECLI numbers, and the second that lists the articles' in that specific case.
    A dataframe is created to filter out any case that does not contain the relevant right.
    A groupby is created and sorted, to prioritise the cases that contain the highest number of relevant rights.
    PostgreSQL query is ran to return all the relevant cases.
    """
    article_groups = pd.read_csv("data/answers_to_articles.csv")
    test_list = ['Prt 7 Art 4 - Right not to be tried or punished twice', 'Art 13 - Right to an effective remedy', 'Prt 7 Art 2 - Right of appeal in criminal matters', 'Prt 4 Art 3 - Prohibition of collective expulsion of aliens', 'Prt 4 Art 1 - Prohibition of imprisonment for debt', 'Art 14 - Prohibition of discrimination', 'Prt 7 Art 3 - Compensation for wrongful conviction', 'Art 11 - Freedom of assembly and association', 'Prt 7 Art 1 - Procedural safeguards relating to expulsion of aliens', 'Prt 4 Art 3 - Prohibition of explusion of nationals', 'Art 1 - Obligation to respect Human Rights', 'Art 7 - No punishment without law', 'Prt 1 Art 1 - Protection of property', 'Prt 7 Art 5 - Equality between spouses', 'Prt 6 Art 1 - Abolition of the death penalty', 'Art 8 - Right to respect for private and family life', 'Art 3 - Prohibition of torture', 'Prt 4 Art 2 - Freedom of movement', 'Art 6 - Right to a fair trial', 'Art 5 - Right to liberty and security']
    filtered_df = article_groups[article_groups.full_name.isin(test_list)]
    article_number_list = filtered_df.short_name.values.tolist()
    df = exploded_articles()
    df_1 = df[df.unnest.isin(article_number_list)]
    ecli_results = df_1.groupby(['ecli']).size().to_frame('count').reset_index().sort_values('count', ascending=False)
    ecli_list = ecli_results['ecli'].to_list()
    sql_query = """
        SELECT url, case_title, importance_number, judgment_date, facts, conclusion
        FROM english_search
        limit 100;
        """
    cursor.execute(sql_query, (tuple(ecli_list),))
    results = cursor.fetchall()
    return results

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
    article_groups = pd.read_csv("data/answers_to_articles.csv")
    # Search_rights are the articles that apply to the user.
    filtered_df = article_groups[article_groups.full_name.isin(search_rights)]
    article_number_list = filtered_df.short_name.values.tolist()
    df = exploded_articles()
    df_1 = df[df.unnest.isin(article_number_list)]
    ecli_results = df_1.groupby(['ecli']).size().to_frame('count').reset_index().sort_values('count', ascending=False)
    ecli_list = ecli_results['ecli'].to_list()
    sql_query = """
        SELECT url, case_title, importance_number, judgment_date, facts, conclusion
        FROM english_search
        WHERE ecli in %s
        limit 100;
        """
    cursor.execute(sql_query, (tuple(ecli_list),))
    results = cursor.fetchall()
    return results

test_results()


