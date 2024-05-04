import logging
from apscheduler.schedulers.background import BackgroundScheduler
from subprocess import Popen, PIPE

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_script(script_path):
    # Run the script using subprocess and capture the output and errors
    process = Popen(['python', script_path], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    # Log the outputs
    if process.returncode == 0:
        logging.info(f"Script {script_path} executed successfully:\n{stdout.decode()}")
    else:
        logging.error(f"Script {script_path} failed with errors:\n{stderr.decode()}")


def start_scheduler():
    scheduler = BackgroundScheduler()

    script_paths = [
        'scraping_files/download_current_soup.py',
        'scraping_files/daily_scrape.py',
        'scraping_files/extract_raw_html.py',
        'scraping_files/extract_case_detail.py',
        'scraping_files/extract_judgment_text.py',
        'scraping_files/display_cases.py'
    ]

    # Schedule all scripts for execution
    for path in script_paths:
        scheduler.add_job(run_script, 'cron', args=[path], hour=3)

    scheduler.start()
