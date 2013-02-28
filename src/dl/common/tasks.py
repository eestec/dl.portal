from celery import task
from django.core.mail import send_mail

@task()
def send_email(subject, message, from_email, recipient_list):
    """
    A wrapper around the Django send_mail function to allow async execution
    by queuing the mails to celery workers.
    """
    send_mail(subject, message, from_email, recipient_list)

