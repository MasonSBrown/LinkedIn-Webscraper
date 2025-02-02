# LinkedIn WebScraper

## NOVELTY
- This scraper continuously checks for job postings that have been listed within the last 10 minutes—capturing fresh opportunities even before LinkedIn pushes out its standard notifications.

## Overview
This project is a web scraper that automates the process of extracting job postings from LinkedIn. It focuses on gathering new Software Engineer Intern listings in the United States. The scraper:
- Logs into LinkedIn using saved cookies for a seamless experience, with a fallback to manual login.
- Parses the LinkedIn jobs page to extract job details.
- Filters listings to only include jobs relevant to internships.
- Utilizes a cache to avoid processing duplicate job alerts.
- Sends SMS notifications using Twilio for new job postings.

## Setup
1. Clone this repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file with the necessary environment variables:
   - `LINKEDIN_EMAIL`
   - `LINKEDIN_PASSWORD`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `YOUR_PHONE_NUMBER`
4. Configure the environment by adjusting any parameters in the script if needed.

## Running the Scraper
Run the scraper using:
```
python scraper.py
```
The script will continuously check for new job postings at regular intervals and notify you via SMS if any new opportunities are found.

## Notes
- The scraper uses Selenium for browser automation and BeautifulSoup for parsing HTML.
- Cookie management is implemented to streamline login sessions.
- Ensure that your Twilio credentials are kept secure.