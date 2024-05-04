import psycopg2
from bs4 import BeautifulSoup
from psycopg2.extras import RealDictCursor
from multiprocessing import Process, Queue, current_process
import queue  # imported for using queue.Empty exception

def connect_psql():
    try:
        conn = psycopg2.connect(database="raw_data_db",
                                host="db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com",
                                user="doadmin", password="AVNS_SbC_UqXYG665R47kxY4", port=25060,
                                sslmode='require')
        return conn
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        exit()

def fetch_ids():
    conn = connect_psql()
    ids = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id 
                FROM raw_html_text
                WHERE NOT EXISTS (
                    SELECT 1 FROM raw_case_detail WHERE raw_case_detail.id = raw_html_text.id
                )
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
                SELECT case_detail_html 
                FROM raw_html_text 
                WHERE id = %s
            """, (id,))
            record = cursor.fetchone()
            if record:
                html_content = record[0]
    except Exception as e:
        print(f"Error fetching HTML content for ID {id}: {e}")
    return html_content

def insert_case_data_as_row(conn, case_id, case_data):
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    table_name = 'raw_case_detail'

    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
    existing_columns = {row['column_name'] for row in cursor.fetchall()}

    for header, value in case_data.items():
        quoted_header = f"\"{header}\""
        if header not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {quoted_header} TEXT;")
            existing_columns.add(header)

    columns = ', '.join(f"\"{col}\"" for col in case_data.keys())
    values = ', '.join(f"%s" for _ in case_data.values())
    insert_query = f"INSERT INTO {table_name} (id, {columns}) VALUES (%s, {values});"

    cursor.execute(insert_query, [case_id, *case_data.values()])
    conn.commit()
    cursor.close()

def process_records(conn, id):
    html_content = fetch_html_content_by_id(conn, id)
    print(id)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        case_details = soup.find_all('div', class_='row noticefield')
        case_data = {}
        for detail in case_details:
            header = detail.find('div', class_='noticefieldheading').get_text(strip=True)
            value_div = detail.find('div', class_='noticefieldvalue')
            values = value_div.find_all('div') if value_div else []
            value_text = ', '.join(value.get_text(strip=True) for value in values if value.get_text(strip=True))
            if not values and value_div:
                value_text = value_div.get_text(strip=True)
            header = make_unique_header(case_data.keys(), header)
            case_data[header] = value_text

        insert_case_data_as_row(conn, id, case_data)

def make_unique_header(existing_headers, header):
    if header not in existing_headers:
        return header
    i = 1
    new_header = f"{header}_{i}"
    while new_header in existing_headers:
        i += 1
        new_header = f"{header}_{i}"
    return new_header

def worker(input_queue):
    conn = connect_psql()  # Open a single connection per worker
    try:
        while True:
            try:
                id = input_queue.get(timeout=1)
                process_records(conn, id)  # Pass the connection to process_records
            except queue.Empty:
                print(f"Process {current_process().name} is exiting.")
                # No more tasks in the queue
                print(f"Process {current_process().name} is exiting.")
                return
    finally:
        conn.close()  # Close the connection when done

def main(ids_to_process):
    num_processes = 2  # Adjust based on your system capabilities and task requirements
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

if __name__ == "__main__":
    max_iterations = 3  # Maximum number of iterations to run the loop
    iteration_count = 0  # Initialize the iteration counter

    while iteration_count < max_iterations:
        ids_to_process = fetch_ids()  # Fetch new IDs to process
        if not ids_to_process:  # Break the loop if no more IDs to process
            print("No more IDs to process.")
            break

        print(f"Iteration {iteration_count + 1}: Processing {len(ids_to_process)} IDs...")
        main(ids_to_process)  # Process the fetched IDs

        iteration_count += 1  # Increment the iteration counter

        if iteration_count < max_iterations:
            print("Checking for new IDs to process...")

    print("Processing completed.")