from email.message import EmailMessage
import ssl
import smtplib
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def send_email():

    email_send = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    
    receiver_email = "doantrungdung2001@gmail.com"
    # Content
    subject = "Thư cảnh báo"
    message = "Vừa có người xuất hiện trong vườn của bạn, hãy kiểm tra"
    
    em = EmailMessage()
    em['From'] = email_send
    em['To'] = receiver_email
    em['subject'] = subject
    em.set_content(message)
    
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_send, password)
        smtp.sendmail(email_send, receiver_email, em.as_string())
        
    
    