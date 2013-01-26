from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.utils import simplejson


def get_or_none(model, **kwargs):
    """
    Gets a Django Model object from the database or returns None if it
    does not exist.
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def redirect_if_logged_in(redirect_url='/'):
    """
    Creates a decorator to redirect a user accessing a view if the user is
    logged in.
    """
    def _decorator(func):
        """
        The actual decorator.
        """
        def _decorated(*args, **kwargs):
            request = args[0]
            if request.user.is_authenticated():
                return HttpResponseRedirect(redirect_url)
            else:
                return func(*args, **kwargs)
        return _decorated
    return _decorator


def render_to_json_response(data, *args, **kwargs):
    """
    Renders the `data` to a JSON response, returning an HttpResponse object
    with the MIME type set to application/json.
    `data` is expected to be serializable by simplejson.
    """
    return HttpResponse(simplejson.dumps(data),
                        content_type='application/json')
