import psycopg2

def connect_psql():
    try:
        conn = psycopg2.connect(database="raw_data_db",
                                host="db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com",
                                user="doadmin", password="AVNS_SbC_UqXYG665R47kxY4", port=25060,
                                sslmode='require')
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        exit()

def create_judgment_text_table():
    conn, cursor = connect_psql()
    table_name = 'display_cases'
    create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            title Text,
            judgment_url TEXT,
            originating_body TEXT,
            importance_level TEXT,
            respondent_state TEXT,
            judgment_date DATE,
            judgment_facts TEXT,
            judgment_conclusion TEXT,
            judgment_full_text TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY (id) REFERENCES all_results_soup(id) ON DELETE CASCADE
        );
    """
    cursor.execute(create_query)
    conn.commit()
    conn.close()

def insert_data():
    conn, cursor = connect_psql()
    insert_query = """
            INSERT INTO display_cases (id, title, judgment_url, originating_body, importance_level, respondent_state, judgment_date,
                    judgment_facts, judgment_conclusion, judgment_full_text)
            SELECT DISTINCT ON (rt.judgment_full_text) 
                rt.id,
                rcd."Title",
                rt.judgment_url,
                rcd."Originating Body",
                rcd."Importance Level",
                rcd."Respondent State(s)",
                TO_DATE(rcd."Judgment Date", 'DD/MM/YYYY') AS judgment_date,
                rt.judgment_facts,
                rt.judgment_conclusion,
                rt.judgment_full_text
            FROM raw_judgment_text rt
            JOIN raw_case_detail rcd ON rt.id = rcd.id
            WHERE rt.language = 'English'
            AND NOT EXISTS (
                SELECT 1 FROM display_cases nt
                WHERE nt.judgment_full_text = rt.judgment_full_text
            )
            ORDER BY rt.judgment_full_text, rt.id
            """
    cursor.execute(insert_query)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_judgment_text_table()
    create_judgment_text_table()
    insert_data()
    print('scraping process complete')

