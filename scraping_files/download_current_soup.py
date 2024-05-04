'''
This script downloads the monthly_soup_temp file, one month from today's date.
'''

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

development = False

options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--disable-extensions")
options.add_argument('--no-sandbox')
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument('--headless')


# Target directory for saving HTML dumps, changed to /monthly_soup_temp
target_directory = 'monthly_soup_temp'
os.makedirs(target_directory, exist_ok=True)

def scroll_function():
    result = None
    scroll_pause_time = 0.5
    screen_height = driver.execute_script("return window.screen.height;")
    print('screen height')
    i = 1
    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        print(i)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        # Break the loop when the height we need to scroll to is larger than the total scroll height
        if (screen_height) * i > scroll_height:
            break


def scroll_function(driver, screen_height):
    scroll_pause_time = 0.5
    i = 1
    while True:
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        if (screen_height) * i > scroll_height:
            break

def get_monthly_url():
    end_date = datetime.now()  # Today's date
    start_date = end_date - timedelta(days=30)  # 30 days before today's date
    return f'https://hudoc.echr.coe.int/eng#{{%22documentcollectionid2%22:[%22JUDGMENTS%22],%22kpdate%22:[%22{start_date.strftime("%Y-%m-%dT00:00:00.0Z")}%22,%22{end_date.strftime("%Y-%m-%dT23:59:59.9Z")}%22]}}'


# Add a function to get the displayed count and scraped results count, if they are not the same then the monthly_soup_temp will
# need to be downloaded again as there was some error
def get_counts(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = soup.find_all(class_='result-item echr-result-item')
    scraped_count = len(results)

    judgments_container = soup.find(lambda tag: tag.name == "span" and "Judgments" in tag.text)
    displayed_count = 0
    if judgments_container:
        branch_counts = judgments_container.find_all('span', class_='branchcount')
        for branch_count in branch_counts:
            count_attribute = branch_count.get('count')
            if count_attribute:
                displayed_count += int(count_attribute)

    return scraped_count, displayed_count

if __name__ == '__main__':
    monthly_url = get_monthly_url()
    file_path = os.path.join(target_directory, 'soup_monthly.html')

    driver = webdriver.Chrome(options=options)
    driver.get(monthly_url)
    driver.implicitly_wait(5)
    time.sleep(5)

    screen_height = driver.execute_script("return window.screen.height;")
    scroll_function(driver, screen_height)

    max_retries = 5
    retries = 0

    while retries < max_retries:
        scroll_function(driver, screen_height)
        scraped_count, displayed_count = get_counts(driver)

        if scraped_count == displayed_count:
            print("Counts match. Saving data...")
            dump = BeautifulSoup(driver.page_source, 'html.parser')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(str(dump))
            break
        else:
            print(f"Counts don't match. Retrying... (Attempt {retries + 1}/{max_retries})")
            driver.refresh()
            time.sleep(5)
            retries += 1

    if retries == max_retries:
        print(f"Failed to get matching counts after {max_retries} retries. Consider manual verification.")

    driver.quit()
    print("Scraping completed.")



