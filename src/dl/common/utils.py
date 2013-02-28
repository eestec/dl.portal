import string
import random

from django.conf import settings
from common.tasks import send_email


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


send_mail = get_send_mail()


def generate_random_string(length=6,
                           char_pool=string.ascii_letters + string.digits):
        return u''.join(random.choice(char_pool) for _ in xrange(length))

