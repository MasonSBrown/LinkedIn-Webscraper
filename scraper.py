import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import schedule
import time

# Twilio Config
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_number'
YOUR_PHONE_NUMBER = 'your_phone_number'

# Set of already seen job IDs
seen_jobs = set()

# Function to scrape LinkedIn jobs
def scrape_jobs():
    url = ("https://www.linkedin.com/jobs/search/"
           "?distance=100&f_TPR=r3600&geoId=102277331&"
           "keywords=software%20engineer%20intern&origin=JOB_SEARCH_PAGE_JOB_FILTER")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract job details (adapt selectors as necessary based on LinkedIn's structure)
    jobs = soup.find_all('a', class_='base-card__full-link')  # Update class selector if required
    
    new_jobs = []
    for job in jobs:
        job_id = job['href']
        if job_id not in seen_jobs:
            seen_jobs.add(job_id)
            new_jobs.append(job)

    if new_jobs:
        notify_user(new_jobs)

# Function to send SMS notifications
def notify_user(new_jobs):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for job in new_jobs:
        job_link = job['href']
        message = client.messages.create(
            body=f"New Software Engineer Internship posted: {job_link}",
            from_=TWILIO_PHONE_NUMBER,
            to=YOUR_PHONE_NUMBER
        )
        print(f"Notification sent for job: {job_link}")

# Schedule the scraper to run periodically
schedule.every(5).minutes.do(scrape_jobs)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
