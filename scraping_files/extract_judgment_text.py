import psycopg2
import re
from bs4 import BeautifulSoup
from lingua import Language, LanguageDetectorBuilder
import queue  # imported for using queue.Empty exception
from multiprocessing import Process, Queue, current_process



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
    table_name = 'raw_judgment_text'
    create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            judgment_url TEXT,
            judgment_facts TEXT,
            judgment_conclusion TEXT,
            judgment_full_text TEXT,
            language TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY (id) REFERENCES all_results_soup(id) ON DELETE CASCADE
        );
    """
    cursor.execute(create_query)
    conn.commit()
    conn.close()


def fetch_ids():
    ## where title does not include translation or french word for translation
    ## or if french, need to state french then translate to english
    conn, cursor = connect_psql()
    ids = []
    try:
        cursor.execute("""
            SELECT id, LOWER("Title")
            FROM raw_case_detail
            WHERE NOT EXISTS (
                SELECT 1 FROM raw_judgment_text WHERE raw_judgment_text.id = raw_case_detail.id
            )
            AND (LOWER("Title") NOT LIKE '%translation%'
            AND LOWER("Title") NOT LIKE '%traduction%')
            ORDER BY id ASC
        """)
        ids = [record[0] for record in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching IDs: {e}")
    finally:
        conn.close()
    return ids

def fetch_html_content_by_id(conn, id):
    html_content = None
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT judgment_html, judgment_url 
                FROM raw_html_text 
                WHERE id = %s
            """, (id,))
            record = cursor.fetchone()
            if record:
                html_content, judgment_url = record[0], record[1]
    except Exception as e:
        print(f"Error fetching HTML content for ID {id}: {e}")
    return html_content, judgment_url

def remove_tags(html):
    # parse html content
    soup = BeautifulSoup(html, "html.parser")

    for data in soup(['style', 'script']):
        # Remove tags
        data.decompose()

    # return data by retrieving the tag content
    return ' '.join(soup.stripped_strings)

def insert_judgement_text(id, judgment_url, judgment_facts, judgment_conclusion, judgment_full_text, language):
    conn, cursor = connect_psql()
    try:
        insert_query = f"""
            INSERT INTO raw_judgment_text
            (id, judgment_url, judgment_facts, judgment_conclusion, judgment_full_text, language)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """
        insert_tuple = (id, judgment_url, judgment_facts, judgment_conclusion, judgment_full_text, language)
        cursor.execute(insert_query, insert_tuple)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def convert_to_english(judgment_full_text, detector):
    language = detector.detect_language_of(judgment_full_text)
    if language is None:
        return None  # Early return if language detection fails
    elif language.iso_code_639_1.name == 'FR':
        return 'French'  # Return 'French' if detected language is French
    else:
        return 'English'  # Default to 'English' if not 'French'


def process_records(conn, cursor, id, detector):
    print(id)
    judgment_facts = ''
    judgment_conclusion = ''
    judgment_full_text = ''
    html_content, judgment_url = fetch_html_content_by_id(conn, id)
    if html_content:
        judgment_full_text = remove_tags(html_content)
        language = convert_to_english(judgment_full_text, detector)

        if language is None:
            print(f"Skipping ID {id} due to undetected or unsupported language.")
            return  # Skip to the next record

        # Modified function to use re.findall() and join matches
        def search_pattern(pattern, text):
            match = pattern.search(text)
            return match.group(1).strip() if match else ""

        def concatenate_matches(matches):
            # Initialize an empty string to store the concatenated result
            concatenated_result = ""

            for match in matches:
                if isinstance(match, tuple):
                    # If the match is a tuple (because of multiple capturing groups), join its elements
                    match_str = ' '.join(match)  # You can change ' ' to whatever delimiter you prefer
                else:
                    # If the match is already a string, use it directly
                    match_str = match

                # Concatenate the match string to the result, with a space in between each match
                concatenated_result += match_str + " "  # You can change ' ' to whatever delimiter you prefer

            # Strip the trailing space and return the result
            return concatenated_result.strip()

        if language == 'English':
            # Search for facts using the updated search_patterns function
            judgment_facts_matches = re.findall(facts_patterns, judgment_full_text)
            judgment_facts = concatenate_matches(judgment_facts_matches)

            judgment_conclusion_matches = re.findall(conclusions_patterns, judgment_full_text)
            judgment_conclusion = concatenate_matches(judgment_conclusion_matches)

        insert_judgement_text(id, judgment_url, judgment_facts, judgment_conclusion, judgment_full_text, language)
    else:
        print('error:', id)


def worker(input_queue):
    conn, cursor = connect_psql()  # Open a single connection per worker
    languages = [Language.ENGLISH, Language.FRENCH]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    try:
        while True:
            try:
                id = input_queue.get(timeout=1)
                process_records(conn, cursor, id, detector)  # Pass the connection to process_records
            except queue.Empty:
                print(f"Process {current_process().name} is exiting.")
                # No more tasks in the queue
                print(f"Process {current_process().name} is exiting.")
                return
    finally:
        conn.close()  # Close the connection when done

def main(ids_to_process):
    num_processes = 1  # Adjust based on your system capabilities and task requirements
    input_queue = Queue()

    # Fill the queue with tasks
    for id in ids_to_process:
        input_queue.put(id)

    processes = []
    for _ in range(num_processes):
        p = Process(target=worker, args=(input_queue,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()  # Wait for all processes to complete


facts_patterns = re.compile(
    r'(?:THE CIRCUMSTANCES OF THE CASE|FACTS)(?:\s+)(?:THE CIRCUMSTANCES OF THE CASE\s+)?(.*?)(?=(?:'
    r'AS TO THE LAW|'
    r'II\.\s*(?=7\.)|PROCEEDINGS BEFORE THE COMMISSION|'
    r'B\.  Relevant domestic law and practice|'
    r'ALLEGED VIOLATION OF ARTICLE 6 § 1 OF THE CONVENTION|'
    r'I\.\s{0,3}ALLEGED VIOLATION OF ARTICLE|'
    r'relevant domestic law and practice|THE LAW|'
    r'AS TO THE REQUEST AS TO STRIKE THE CASE OUT OF THE LIST|'
    r'FINAL SUBMISSIONS MADE TO THE COURT|B\.  The proceedings in the courts|'
    r'II\.(?i:\s+RELEVANT DOMESTIC LAW)|'  
    r'RELEVANT DOMESTIC AND INTERNATIONAL LAW|'
    r'(?i:\s+RELEVANT DOMESTIC LAW AND PRACTICE)|'
    r'RELEVANT LEGAL FRAMEWORK AND PRACTICE|'
    r'II\.\s*RELEVANT|II\.\s+RELEVANT DOMESTIC LAW|RELEVANT DOMESTIC LAW|relevant domestic law))', re.DOTALL
)


conclusions_patterns = re.compile(
    r'(?:FOR THESE REASONS,?(?: [A-Z]+,?)*|for these reasons, the court|'
    r'THE COURT\s+Unanimously,|THE COURT[,]?|(?i:THE COURT UNANIMOUSLY)|(?i:FOR THOSE REASONS, THE COURT,))\s+(.*?)(?=(Done in|Signed:|President))',
    re.DOTALL
)

##for these reasons need to be in not caps


if __name__ == "__main__":
    create_judgment_text_table()
    ids_to_process = fetch_ids()
    print('length of processing ids:', len(ids_to_process))
    main(ids_to_process)
