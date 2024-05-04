'''
Scraped case details and judgments form the headline text

noticed that the headline texts, url that takes you to the case does not always work
as sometimes the cases are not in the language of the headline - these are roughly 24473 headline items
'''
import psycopg2
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import re
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from urllib.parse import urlparse, unquote
from multiprocessing import Process, Queue, current_process
import queue  # imported for using queue.Empty exception
from selenium.common.exceptions import StaleElementReferenceException
import os


options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--disable-extensions")
options.add_argument('--no-sandbox')
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument('--headless')


# Connection to Postgres Database
def connect_psql():
    return psycopg2.connect(database="raw_data_db",
                                host="db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com",
                                user="doadmin", password="AVNS_SbC_UqXYG665R47kxY4", port=25060,
                                sslmode='require')


def explicit_wait_title(driver):
    #Selenium Explicit Wait set with 5 second timeout and on the location of the case title element
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="notice"]/div/div[5]/div/div[2]/div')))


def explicit_wait_language(driver):
    #Selenium Explicit Wait set with 5 second timeout and on the location of the available in language element
    element_xpath = '//*[@id="document"]/div/div[2]/div[2]/div[2]/a'
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, element_xpath)))
    return element_xpath


def scroll_function(driver):
    scroll_pause_time = 0.5
    screen_height = driver.execute_script("return window.screen.height;")
    i = 1
    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        # Break the loop when the height we need to scroll to is larger than the total scroll height
        if (screen_height) * i > scroll_height:
            break


def catch_error(id_foreign, error_message, error_location):
    target_directory = 'error_files'
    os.makedirs(target_directory, exist_ok=True)

    error_log_path = 'error_files/'

    with open('error_files/extraction_errors.csv', 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        # Check if the file is empty to write the header
        file.seek(0, 2)  # Move the cursor to the end of the file
        if file.tell() == 0:  # If the file is empty, write the header
            writer.writerow(['database_id', 'error_type', 'error_location'])
        writer.writerow([id_foreign, error_message, error_location])

def create_raw_html_text_table():
    conn, cursor = connect_psql()
    table_name = 'raw_html_text'
    create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            col5 TEXT,
            case_detail_html TEXT,
            case_detail_url TEXT,
            judgment_html TEXT,
            judgment_url TEXT,
            PRIMARY KEY (id),
            FOREIGN KEY (id) REFERENCES all_results_soup(id) ON DELETE CASCADE
        );
    """
    cursor.execute(create_query)

    # SQL to check if 'new_item_id' column exists
    check_column_query = f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='{table_name}' AND column_name='non_headline_item_id';
    """
    cursor.execute(check_column_query)
    result = cursor.fetchone()

    # If 'new_item_id' column does not exist, add it
    if not result:
        add_column_query = f"""
            ALTER TABLE {table_name}
            ADD COLUMN non_headline_item_id TEXT;
        """
        cursor.execute(add_column_query)

    conn.commit()
    conn.close()

def extract_case_detail(driver, col5_id_value, id_foreign):
    # Set Selenium Driver Options
    try:
        driver.implicitly_wait(0.5)
        case_detail_url = str('https://hudoc.echr.coe.int/#{%22tabview%22:[%22notice%22],%22itemid%22:[%22' + col5_id_value + '%22]}')
        driver.get(case_detail_url)
        explicit_wait_title(driver)
        scroll_function(driver)
        #Click through any 'more' elements to expand the entire list
        more_elements = driver.find_elements(By.CLASS_NAME, 'moreword')
        if more_elements:
            for j in more_elements:
                driver.execute_script("arguments[0].scrollIntoView(true);", j)
                time.sleep(0.5)
                j.click()
        case_detail_html = driver.page_source
        return case_detail_html, case_detail_url

    except Exception as e:
        error_message = str(e)
        catch_error(id_foreign, error_message, 'case_detail')
        raise

def extract_content_from_url(url):
    # Parsing the URL fragment (the part after '#')
    parsed_url = urlparse(url)
    fragment = parsed_url.fragment

    # Finding the last occurrence of '[' and ']'
    start_index = fragment.rfind('[')
    end_index = fragment.rfind(']')

    # Extracting and decoding the content within the last square brackets
    if start_index != -1 and end_index != -1 and start_index < end_index:
        content = fragment[start_index+1:end_index]
        decoded_content = unquote(content).strip('"')
        return decoded_content

    # Return None or an empty string if no content is found
    return None

@contextmanager
def webdriver_context():
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def extract_judgment_text(driver, col5_id_value, id_foreign):
    # Set Selenium Driver Options
    try:
        case_detail_url = ''
        judgment_html = ''
        judgment_url = ''
        case_detail_html = ''
        french_url = ''
        english_url = ''
        new_judgment_url = ''
        judgment_url = f'https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id={col5_id_value}'
        driver.get(judgment_url)
        time.sleep(1)
        judgment_html = driver.page_source
        if judgment_html == '<html><head></head><body></body></html>':
            non_headline_item_id = 'Not Found'
            tab_view_url = str('https://hudoc.echr.coe.int/eng#{%22tabview%22:[%22document%22],%22itemid%22:[%22' + col5_id_value + '%22]}')
            driver.get(tab_view_url)
            element_xpath = explicit_wait_language(driver)
            print('being redirected as original item_id is not valid')
            retry_attempts = 5  # Set the number of retries
            for attempt in range(retry_attempts):
                try:
                    elements = driver.find_elements(By.XPATH, element_xpath)
                    time.sleep(0.5)
                    for element in elements:
                        if element.text == 'English':
                            judgment_html = ''
                            english_url = element.get_attribute('href')
                            non_headline_item_id = extract_content_from_url(english_url)
                            new_judgment_url = f'https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id={non_headline_item_id}'
                            driver.get(new_judgment_url)
                            time.sleep(1)
                            judgment_html = driver.page_source
                            return judgment_html, new_judgment_url, non_headline_item_id
                    for element in elements:
                        if element.text == 'French':
                            judgment_html = ''
                            french_url = element.get_attribute('href')
                            non_headline_item_id = extract_content_from_url(french_url)
                            new_judgment_url = f'https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id={non_headline_item_id}'
                            driver.get(new_judgment_url)
                            time.sleep(1)
                            judgment_html = driver.page_source
                            return judgment_html, new_judgment_url, non_headline_item_id
                    # Handle the case where neither English nor French judgment texts are found
                    if not non_headline_item_id:
                        catch_error(id_foreign, "No English or French judgment text found", 'judgment')
                        return judgment_html, judgment_url, non_headline_item_id
                    break
                except StaleElementReferenceException:
                    if attempt == retry_attempts - 1:  # Last attempt
                        raise  # Reraise the exception if it's the last attempt
                    time.sleep(1)  # Wait before retrying




        # Return the original judgment HTML if it was not empty
        return judgment_html, judgment_url, None

    except Exception as e:
        error_message = str(e)
        catch_error(id_foreign, error_message, 'judgment')
        raise



def insert_case_details_db(conn, cursor, id_foreign, col5_id_value, case_detail_html, case_detail_url, judgment_html, judgment_url, non_headline_item_id):
    #Insertion of all extracted case details into the Postgres Database
    insert_query = """ INSERT INTO raw_html_text
                        (id,
                        col5,
                        case_detail_html,
                        case_detail_url,
                        judgment_html, 
                        judgment_url,
                        non_headline_item_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING;
                    """
    insert_tuple = (id_foreign, col5_id_value, case_detail_html, case_detail_url, judgment_html, judgment_url, non_headline_item_id)
    cursor.execute(insert_query, insert_tuple)
    conn.commit()



def extract_all(result_item):
    driver = webdriver.Chrome(options=options)
    col5_id_value = re.search(r'\["([^"]*)"\](?=[^\[\]]*$)', result_item[1]).group(1) if re.search(
        r'\["([^"]*)"\](?=[^\[\]]*$)', result_item[1]) else None
    id_foreign = result_item[0]
    try:
        case_detail_html, case_detail_url = extract_case_detail(driver, col5_id_value, id_foreign)
        judgment_html, judgment_url, non_headline_item_id = extract_judgment_text(driver, col5_id_value, id_foreign)
    except Exception as e:
        print(f'Skipping insertion for {id_foreign} due to extraction failure: {e}')
        driver.close()
        driver.quit()
        return
    with connect_psql() as conn:
        with conn.cursor() as cursor:
            insert_case_details_db(conn, cursor, id_foreign, col5_id_value, case_detail_html, case_detail_url, judgment_html, judgment_url, non_headline_item_id)
    conn.close()
    print('inserted', col5_id_value)
    driver.close()
    driver.quit()

def worker(input_queue):
    while True:
        try:
            # Try to get a task from the queue, timeout after 1 second
            result_item = input_queue.get(timeout=1)
        except queue.Empty:
            # No more tasks in the queue
            print(f"Process {current_process().name} is exiting.")
            return
        extract_all(result_item)


def main(iteration_list):
    num_processes = 2  # Adjust based on your system capabilities and task requirements
    input_queue = Queue()

    # Fill the queue with tasks
    for item in iteration_list:
        input_queue.put(item)

    processes = []
    for _ in range(num_processes):
        p = Process(target=worker, args=(input_queue,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()  # Wait for all processes to complete


if __name__ == "__main__":
    def return_headline_href():
        conn, cursor = connect_psql()
        sql_query = """SELECT id, col5
                       FROM all_results_soup
                       WHERE col5 NOT ILIKE '%pdf%'
                       ORDER BY id ASC 
                       """
        cursor.execute(sql_query)
        headline_href = cursor.fetchall()
        conn.close()
        return headline_href


    def insertion_skip():
        conn, cursor = connect_psql()
        # Returns boolean when a url already exists in the database
        exists_query = """SELECT id FROM raw_html_text"""
        cursor.execute(exists_query)
        skip_list = [r[0] for r in cursor.fetchall()]
        conn.close()
        return skip_list

    def connect_psql():
        try:
            conn = psycopg2.connect(database="raw_data_db",
                                    host="db-postgresql-fra1-kyr-0001-do-user-12476250-0.b.db.ondigitalocean.com",
                                    user="doadmin", password="AVNS_SbC_UqXYG665R47kxY4", port=25060,
                                    sslmode='require')
            print("Connected to the database")
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            exit()

    conn, cursor = connect_psql()
    create_raw_html_text_table()
    headline_href = return_headline_href()
    skip_list = insertion_skip()
    iteration_list = [(id_foreign, value) for id_foreign, value in headline_href if id_foreign not in skip_list]

    main(iteration_list)




