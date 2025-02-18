import json
import os
import re
import pickle
import base64  # Added for decoding cookies from COOKIES_B64
from time import sleep

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException, TwilioException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

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

def load_cookies(driver):
    cookies_b64 = os.getenv("COOKIES_B64")
    if cookies_b64:
        try:
            cookie_bytes = base64.b64decode(cookies_b64)
            cookies = pickle.loads(cookie_bytes)
            driver.get("https://www.linkedin.com")  # Open LinkedIn first
            sleep(2)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print("🔑 Cookies loaded from COOKIES_B64 secret successfully!")
            driver.refresh()
            sleep(3)
            return
        except Exception as e:
            print(f"Error loading cookies from COOKIES_B64: {e}")
    # Fallback: try to load from cookies.b64 file in the repository
    if os.path.exists("cookies.b64"):
        try:
            with open("cookies.b64", "r", encoding="utf-8") as file:
                file_b64 = file.read().strip()
            cookie_bytes = base64.b64decode(file_b64)
            cookies = pickle.loads(cookie_bytes)
            driver.get("https://www.linkedin.com")
            sleep(2)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print("🔑 Cookies loaded from cookies.b64 file successfully! 2")
            driver.refresh()
            sleep(3)
            return
        except Exception as e:
            print(f"Error loading cookies from cookies.b64 file: {e}")
    print("❌ Cookies not available or failed.")
    if os.getenv("LINKEDIN_EMAIL") and os.getenv("LINKEDIN_PASSWORD"):
        linkedin_login(driver)
    else:
        print("❌ Missing LinkedIn credentials; cannot login manually.")
        exit(1)

def linkedin_login(driver):
    # Ensure credentials are provided
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        raise ValueError("Missing LinkedIn credentials: set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables.")
    
    driver.get("https://www.linkedin.com/login")
    sleep(3)  # Allow page to load
    email_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")
    email_input.send_keys(email)
    password_input.send_keys(password)
    password_input.submit()
    sleep(5)  # Wait for login to complete


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

    # Log into LinkedIn using cookies; if they fail, perform manual login
    load_cookies(driver)  # Use cookies login as first attempt

    # Open LinkedIn jobs page
    url = "https://www.linkedin.com/jobs/search?keywords=Software%20Engineer%20Intern&location=United%20States&geoId=103644278&f_TPR=r600&position=1&pageNum=0"

    driver.get(url)
    sleep(5)  # Allow time for page to load

    # Extract page source and pass to BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract the ul block and all li entities
    ul_blocks = soup.find_all("ul")
    li_entities = ul_blocks[7].find_all("li")

    # Load cache
    these_seen_jobs = load_cache()

    new_jobs = []
    wanted_text = ''

    for idx, li in enumerate(li_entities):
        li_text = li.text
        if li_text == "\n\nPromoted\n\n":
            # Process the current segment
            text = wanted_text
            groups = [s for s in re.split(r'\s{2,}', text.strip()) if s]
            groups[0] = groups[0][:len(groups[0]) // 2]
            job_id = groups[0] + groups[1]  # Title plus company name
            # New check: add job only if it contains 'intern' (case-insensitive)
            if "intern" in job_id.lower() and job_id not in these_seen_jobs:
                these_seen_jobs.add(job_id)
                new_jobs.append(" ".join(groups))
        else:
            if idx == 0:
                wanted_text = li_text

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
    while True:
        scrape_jobs()
        print("Waiting 10 minutes before next check...")
        sleep(600)

if __name__ == "__main__":
    main()
