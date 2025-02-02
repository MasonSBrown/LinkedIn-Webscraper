import json
import os
from time import sleep

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException, TwilioException
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables from .env file
load_dotenv()

# Twilio Config (KEEP PRIVATE THIS IS SENSITIVE INFORMATION)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

# Track seen jobs
seen_jobs = set()

CACHE_FILE = "job_cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return set(json.load(file))
    return set()


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(list(cache), file)


def clean_job_text(li_entity):
    title = li_entity.find("h3", class_="base-search-card__title").get_text(strip=True)
    company = li_entity.find("h4", class_="base-search-card__subtitle").get_text(
        strip=True
    )
    location = li_entity.find("span", class_="job-search-card__location").get_text(
        strip=True
    )
    time_posted = li_entity.find("time").get_text(strip=True)
    return f"{title} at {company}, {location} - {time_posted}"


def scrape_jobs():
    print("🚀 Launching browser...")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # Start browser
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    # Open LinkedIn jobs page
    url = "https://www.linkedin.com/jobs/search?keywords=Software%20Engineer%20Intern&location=United%20States&geoId=103644278&f_TPR=r15000&position=1&pageNum=0"

    driver.get(url)
    sleep(5)  # Allow time for page to load

    # Extract page source and pass to BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract the ul block and all li entities
    ul_block = soup.find("ul", class_="jobs-search__results-list")
    li_entities = ul_block.find_all("li") if ul_block else []

    # Load cache
    these_seen_jobs = load_cache()

    new_jobs = []
    for li in li_entities:
        job_text = clean_job_text(li)
        job_id = job_text.split(" - ", maxsplit=1)[0]  # Use job title and company as unique ID

        if job_id not in these_seen_jobs:
            these_seen_jobs.add(job_id)
            new_jobs.append(job_text)

    driver.quit()  # Close browser

    if new_jobs:
        print("✅ Found new jobs:", new_jobs)
        notify_user(new_jobs)
        save_cache(these_seen_jobs)
    else:
        print("🔍 No new jobs to notify.")


# Send SMS Notification
def notify_user(new_jobs):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    job_list = "\n".join(new_jobs[:5])  # Limit SMS to 5 jobs
    message_body = f"New Software Engineer Intern jobs:\n{job_list}"

    try:
        client.messages.create(
            body=message_body, from_=TWILIO_PHONE_NUMBER, to=YOUR_PHONE_NUMBER
        )
    except (TwilioRestException, TwilioException) as e:
        print(f"❌ Twilio error: {e}")


def main():
    scrape_jobs()


if __name__ == "__main__":
    main()
