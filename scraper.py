import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import schedule
import time

# Twilio Config (Replace with actual values)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_number'
YOUR_PHONE_NUMBER = 'your_phone_number'

# Track seen jobs
seen_jobs = set()

# Function to scrape LinkedIn jobs
def scrape_jobs():
    url = ("https://www.linkedin.com/jobs/search/"
           "?distance=100&f_TPR=r3600&geoId=102277331&"
           "keywords=software%20engineer%20intern&origin=JOB_SEARCH_PAGE_JOB_FILTER")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching LinkedIn jobs: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract job links (Adjust the selector if needed)
    jobs = soup.find_all('a', class_='base-card__full-link')

    new_jobs = []
    for job in jobs:
        job_url = job['href']
        job_id = job_url.split('?')[0]  # Extract stable job ID (removing query params)

        if job_id not in seen_jobs:
            seen_jobs.add(job_id)
            new_jobs.append(job_url)

    if new_jobs:
        notify_user(new_jobs)

# Function to send SMS notifications
def notify_user(new_jobs):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Combine multiple jobs into one message
    job_list = "\n".join(new_jobs[:5])  # Limit to 5 to fit SMS length
    message_body = f"New Software Engineer Intern jobs:\n{job_list}"

    try:
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=YOUR_PHONE_NUMBER
        )
        print(f"Notification sent! SID: {message.sid}")
    except Exception as e:
        print(f"Error sending Twilio message: {e}")

# Schedule the scraper to run every 5 minutes
schedule.every(5).minutes.do(scrape_jobs)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
