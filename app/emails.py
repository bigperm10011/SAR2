from flask_mail import Message
from app import mail
from flask import render_template
from flask_login import current_user
from app.models import Srep, Leaver, Suspect
from app import app

def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)

def find_notification(found):
    send_email("Previous Bloomberg User Found!",
               sender=app.config['ADMINS'][0],
               recipients=[current_user.repemail],
               html_body=render_template("found_mail.html",
                               user=current_user, found=found))

def scraperesult(results):
    send_email("SAR Scrape Results",
               sender=app.config['ADMINS'][0],
               recipients=[current_user.repemail],
               html_body=render_template("scrape_report.html",
                               user=current_user, results=results))
