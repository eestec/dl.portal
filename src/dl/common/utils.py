import string
import random

from django.conf import settings
from common.tasks import send_email

from django.http import HttpResponse
from django.utils import simplejson

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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


def render_to_json_response(data, *args, **kwargs):
    """
    Renders the `data` to a JSON response, returning an HttpResponse object
    with the MIME type set to application/json.
    `data` is expected to be serializable by simplejson.
    """
    return HttpResponse(simplejson.dumps(data),
                        content_type='application/json')


def paginate_video_set(query_set, page_number=1):
    VIDEOS_PER_PAGE = 6
    paginator = Paginator(query_set, VIDEOS_PER_PAGE)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = None
    return page
