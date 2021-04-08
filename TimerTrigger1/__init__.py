import datetime
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
import time

import azure.functions as func
import requests
from bs4 import BeautifulSoup

from . import config

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)  
    url = "https://www.nj.gov/health/cd/statistics/covid/"
    
    while True:         
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Get the Week Ending date from the link/pdf
        ct= soup.findAll("div", {"class" : "mainText"})
        weekEnding = ct[1].findAll("li")[0].find("a").string # There are two mainText classes, grab the 2nd one, the first list item, the first 'a' tag
        x = weekEnding.split("week ending ")
        y = x[1].replace(")", "") # March 6, 2021
        # Convert string to datetime.date object
        week_ending = datetime.datetime.strptime(y, "%B %d, %Y").date()
        # Build the full url
        href = ct[1].findAll("li")[0].find("a")['href']
        fullUrl = "https://nj.gov" + href
        # Get the last Saturday based on todays date
        today = datetime.date.today()
        idx = (today.weekday() + 1)
        last_saturday = today - datetime.timedelta(7+idx-6)
        
        if last_saturday==week_ending:
            logging.info("A new CALI Report has been posted.")
            context = ssl.create_default_context()
            with smtplib.SMTP("smtp.office365.com", 587) as server:
                sender_email = config.EMAIL_USERNAME
                receiver_email = config.EMAIL_USERNAME
                password= config.EMAIL_PASSWORD
                message = MIMEMultipart("alternative")
                message["Subject"] = "***New CALI Report***"
                message["From"] = sender_email
                message["To"] = receiver_email
                # Create the plain-text and HTML version of your message
                text = """\
                An HTML email could not be delivered.  Please reply to this email at your earliest convenience."""
                html =  '''
                <h1>A new CALI report has been posted to the NJ Covid Website.  See here:</h1>
                '''
                html+=fullUrl
                # Turn these into plain/html MIMEText objects
                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")

                # Add HTML/plain-text parts to MIMEMultipart message
                # The email client will try to render the last part first
                message.attach(part1)
                message.attach(part2)
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            break
        else:
            logging.info("Nothing new to see here.")
        time.sleep(300)
        
        