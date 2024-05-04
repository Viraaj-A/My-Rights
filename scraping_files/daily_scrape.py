import time
import os
import psycopg2
from bs4 import BeautifulSoup
import re


"""
This script is designed to run for a 1-month duration starting from the current date. Due to the HUDOC database's
 inconsistencies and the retrospective addition of cases, it is necessary to perform checks to ensure comprehensive 
 case capture. Ideally, the search would encompass the entire history of HUDOC daily to be fully effective; however, 
 this approach is impractical. Therefore, this adjusted strategy aims to maintain an efficient yet thorough collection 
 process within the feasible bounds.
"""
def existing_cases():
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

    def extract_existing_items():
        query = "SELECT col4, col5, col6 FROM all_results_soup"
        cursor.execute(query)
        rows = cursor.fetchall()
        existing_results = [{"col4": row[0], "col5": row[1], "col6": row[2]} for row in rows]
        return existing_results

    def table_mapping():
        query = "SELECT mapped_name, actual_name FROM all_results_soup_mapping"
        cursor.execute(query)
        rows = cursor.fetchall()
        table_mapping = {row[0]: row[1] for row in rows}
        return table_mapping


    conn, cursor = connect_psql()
    existing_results = extract_existing_items()
    table_mapping = table_mapping()
    return existing_results, table_mapping, conn, cursor


def load_soup(soup_directory):
    # Assuming the soup file has a consistent naming convention, e.g., 'soup_monthly.html'
    filename = 'soup_monthly.html'
    filepath = os.path.join(soup_directory, filename)

    # Check if the file exists before attempting to open it
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            return soup
    else:
        print(f"File {filename} not found in {soup_directory}.")
        return None


def extract_element_to_check(elements):
    element_values = []
    for selector in checking_selectors:
        if '[href]' in selector:
            modified_selector = selector.split('[')[0]
            inner_element = element.select_one(modified_selector)  # Use select_one to find the first match
            value = inner_element['href'] if inner_element else ''
        else:
            inner_element = element.select_one(selector)  # Use select_one to find the first match
            value = inner_element.get_text() if inner_element else ''
        element_values.append(value)
    element_dict = {'col4': element_values[0], 'col5': element_values[1], 'col6': element_values[2]}
    return element_dict


def match_in_existing_results(element_dict, existing_results):
    for existing_dict in existing_results:
        # Compare the element dictionary with each dictionary in existing_results
        if all(element_dict[key] == existing_dict[key] for key in ['col4', 'col5', 'col6']):
            return True  # Match found
    return False  # No match found


def extract_data(element, selectors):
    element_data = {}

    for selector in selectors:
        # Check if the selector includes a language part and an href
        if '][' in selector and '[href]' in selector:
            parts = selector.split('[')
            css_part = parts[0]
            lang_part = parts[1].rstrip(']')
            attr_part = parts[2].rstrip(']')

            # Select elements using the valid CSS part
            inner_elements = element.select(css_part)


            # Filter elements based on text content matching the language
            for el in inner_elements:
                if el.get_text() == lang_part:
                    href_value = el['href']
                    href_value = clean_text(href_value)
                    element_data[selector] = href_value
                    break

        elif '[href]' in selector:
            # Handle selectors with only [href]
            modified_selector = selector.split('[')[0]
            inner_element = element.select_one(modified_selector)
            href_value = inner_element['href'] if inner_element else ''
            href_value = clean_text(href_value)
            element_data[selector] = href_value

        else:
            # Handle selectors without any square brackets
            inner_element = element.select_one(selector)
            text_value = inner_element.get_text() if inner_element else ''
            text_value = clean_text(text_value)
            element_data[selector] = text_value

    return element_data

def clean_text(text):
    # Remove escape-like sequences and unnecessary whitespace
    text = re.sub(r'\\.', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('\xa0', ' ')
    return text

if __name__ == '__main__':
    existing_results, table_mapping, conn, cursor = existing_cases()

    # Create selectors to identify whether the current element/case already exists in
    columns = ['col4', 'col5', 'col6']
    checking_selectors = [table_mapping[column] for column in columns if column in table_mapping]

    # Load monthly soup file to scrape
    soup_directory = 'monthly_soup_temp'
    soup = load_soup(soup_directory)

    elements_to_scrape = []
    single_page_view_results = soup.find_all(class_='result-item echr-result-item')  # Use CSS selectors to find elements
    for element in single_page_view_results:
        element_with_text = element.find_all(string=lambda text: text and text.strip())
        element_dict = extract_element_to_check(element_with_text)
        found = match_in_existing_results(element_dict, existing_results)

        if not found:
            elements_to_scrape.append(element)  # Append the element dictionary, not the element itself

    print(len(elements_to_scrape))

    # Initialize test as an empty list
    cases_to_insert = []
    for element_to_insert in elements_to_scrape:
        # Extract data for each element and append the resulting dictionary to test
        case_data = extract_data(element_to_insert, table_mapping.values())
        cases_to_insert.append(case_data)

    mapped_cases = []
    for case in cases_to_insert:
        mapped_dict = {key: case.get(value, None) for key, value in table_mapping.items()}
        mapped_cases.append(mapped_dict)

    try:
        for item in mapped_cases:
            # Add daily_scrape text to distinguish source of data
            item['col1'] = 'daily_scrape'  # Set the value for 'col1' directly in the item

            # Construct the columns and placeholders strings
            columns = ', '.join(item.keys())
            placeholders = ', '.join(['%s'] * len(item))

            # Construct the INSERT INTO statement
            insert_query = f'INSERT INTO all_results_soup ({columns}) VALUES ({placeholders})'

            # Execute the query with the values
            cursor.execute(insert_query, list(item.values()))

            # Commit the transaction
        conn.commit()

    except Exception as e:
        # If an error occurs, print the error message and rollback the transaction
        print(f"An error occurred: {e}")
        conn.rollback()

    finally:
        # Close the cursor and connection to clean up
        cursor.close()
        conn.close()