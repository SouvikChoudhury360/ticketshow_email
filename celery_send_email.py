import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery
from celery.schedules import crontab

# Initialize Celery with Redis as the broker
celery = Celery('celery_send_email', broker='rediss://red-cj85cfdjeehc73a61p90:n3qx1b4MCMGmE1MsTFGcOYaQPKqiA4S3@oregon-redis.render.com:6379')

# Define the API endpoint to fetch emails
api_url = "https://ticketshow-api.onrender.com/reminder"

# Task to fetch emails from the API
@celery.task
def fetch_emails_from_api():
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch emails from the API: {e}")
        return []

# Task to send the emails
@celery.task
def send_emails(emails):
    # Email configuration (replace with your email settings)
    sender_email = "ostorage12@gmail.com"
    sender_password = "lemonmomo#2003"
    smtp_server = "smtp-relay.brevo.com"
    smtp_port = 587

    message = MIMEMultipart()
    message['From'] = sender_email
    message['Subject'] = "TicketShow"
    body = "You have'nt booked a ticket for a while"
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)

            for recipient in emails:
                message['To'] = recipient
                server.sendmail(sender_email, recipient, message.as_string())

        print("Emails sent successfully!")
    except Exception as e:
        print(f"Failed to send emails: {e}")

# Schedule the task to run at 7 PM every day
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run the fetch_emails_from_api task every day at 6:30 PM
    sender.add_periodic_task(
        crontab(hour=18, minute=30),
        fetch_emails_from_api.s(),
        name='fetch_emails_from_api_task'
    )

    # Run the send_emails task every day at 7 PM
    sender.add_periodic_task(
        crontab(hour=15, minute=25),
        send_emails.s(),
        name='send_emails_task'
    )

if __name__ == '__main__':
    celery.start()
