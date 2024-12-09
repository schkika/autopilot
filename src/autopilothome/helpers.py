from django.core.mail import send_mail
from django.conf import settings

def email(subject, message, recipient):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [ recipient ]
    send_mail( subject, message, email_from, recipient_list )