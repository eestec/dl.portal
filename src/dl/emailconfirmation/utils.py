from django.conf import settings
from emailconfirmation.tasks import send_email

def get_send_mail():
    """
    A function to return a send_mail function suitable for use in the app.
    Uses the async worker queue if allowed, otherwise uses the django
    blocking send_mail function.
    """
    if getattr(settings, 'DL_USE_ASYNC', False):
        def send_mail(*args, **kwargs):
            send_email.delay(*args, **kwargs)
    else:
        from django.core.mail import send_mail as _send_mail
        def send_mail(*args, **kwargs):
            return _send_mail(*args, **kwargs)
    return send_mail
