"""
EESTEC International Distance Learning - Accounts.
Views for the accounts application.
"""
from django.db import IntegrityError

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest

from django.utils import simplejson
from django.utils.decorators import method_decorator

from django.template import RequestContext

from django.shortcuts import render_to_response
from django.shortcuts import redirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic.edit import UpdateView
from django.views.generic.base import View

# Generic view for user login provided by contrib.auth
from django.contrib import messages
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required, permission_required

from distance_learning.models import Video

from emailconfirmation.models import EmailAddress

from accounts.models import Student, University, Company
from accounts.forms import get_form_for_model
from accounts.utils import redirect_if_logged_in, get_or_none

from common.utils import render_to_json_response

import dl.settings as settings

@redirect_if_logged_in('/')
def custom_login(request, **kwargs):
    """
    A view which tries to log in a user or shows the appropriate login
    form.  It wraps the contrib.auth login view to first check if the user
    is already logged in so as not to show the login form if one is.
    """
    # TODO: Render a different template for an AJAX call
    return login(request, **kwargs)


@redirect_if_logged_in('/')
def _generic_register_member(request, form_class, registration_view_name):
    """
    A helper function which handles generic member registration parametrized
    by the form class used for the particular member model.
    """
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_member = None
            try:
                new_member = form.save()
            except IntegrityError:
                # TODO: Redirect to a registration failed page
                pass
            # Additional registration logic: send a confirmation email
            if new_member is not None:
                if settings.SEND_CONFIRMATION_EMAIL:
                    # Activation based on email confirmation
                    EmailAddress.objects.add_email(
                        new_member.userprofile.user,
                        new_member.cast().email)
                else:
                    # Immediate activation, no email confirmation
                    new_member.active = True
                    new_member.save()
            return HttpResponseRedirect('/')
    else:
        form = form_class()
    return render_to_response(
        'registration/register.html',
        {'form': form,
         'registration_view_name': registration_view_name},
        context_instance=RequestContext(request))


def register_student(request):
    """ 
    A view for registering new Student members.
    """
    # Delegates to the generic registration method with the apropriate
    # parameters set.
    return _generic_register_member(request,
                                    get_form_for_model(Student),
                                    'register-student')


def register_university(request):
    """
    A view for registering a new University member.
    """
    return _generic_register_member(request,
                                    get_form_for_model(University),
                                    'register-university')


def register_company(request):
    """
    A view for registering a new Company member.
    """
    return _generic_register_member(request,
                                    get_form_for_model(Company),
                                    'register-company')


@login_required
def add_favorite(request):
    profile = request.user.get_profile()
    if request.method == "GET":
        return redirect('profile-get-favorites', page_number=1)
    if 'video_id' not in request.POST:
        return HttpResponseBadRequest()
    try:
        video_id = int(request.POST['video_id'])
    except ValueError:
        return HttpResponseBadRequest()
    video = get_or_none(Video, pk=video_id)
    if video is None:
        status = {
            'status': 'fail',
            'reason': 'Video does not exist.',
        }
    else:
        profile.favorite_videos.add(video)
        status = {
            'status': 'ok',
        }
    return HttpResponse(simplejson.dumps(status),
                        content_type='application/json')


@login_required
def add_watch_later(request):
    profile = request.user.get_profile()
    if request.method != 'POST' or 'video_id' not in request.POST:
        return HttpResponseBadRequest()
    try:
        video_id = int(request.POST['video_id'])
    except ValueError:
        return HttpResponseBadRequest()
    video = get_or_none(Video, pk=video_id)
    if video is None:
        status = {
            'status': 'fail',
            'reason': 'Video does not exist.',
        }
    else:
        profile.watch_later_videos.add(video)
        status = {
            'status': 'ok',
        }
    return HttpResponse(simplejson.dumps(status),
                        content_type='application/json')


def _paginate_video_set(query_set, page_number):
    VIDEOS_PER_PAGE = 6
    paginator = Paginator(query_set, VIDEOS_PER_PAGE)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = None
    return page


def _build_response(page):
    """
    Builds a response as a JSON encoded dictionary with a list of videos
    and additionaly information about total videos found, the current page.
    """
    videos = [] if page is None else page.object_list
    response = {
        'status': 'ok',
        'videos': [video.to_dict() for video in videos],
        'total': page.paginator.count,
        'page': page.number,
    }
    if page is not None:
        if page.has_next():
            response['next'] = page.next_page_number()
        if page.has_previous():
            response['prev'] = page.previous_page_number()
    return simplejson.dumps(response)


@login_required
def get_favorites(request, page_number):
    """
    A view returns a list of favorite Videos for the currently signed in user.
    It returns HTML for "normal" requests and JSON for AJAX requests.
    """
    if request.method != "GET":
        return HttpResponseBadRequest()
    profile = request.user.userprofile
    page = _paginate_video_set(profile.favorite_videos.all(),
                               page_number)
    if request.is_ajax():
        return HttpResponse(
            _build_response(page),
            content_type='application/json')
    else:
        if page is None:
            raise Http404
        return render_to_response(
            'distance_learning/profile.html',
            {'videos': page,
             'result_type': 'favorites',
             'pages': range(page.paginator.num_pages)},
            context_instance=RequestContext(request))


class FavoritesView(View):
    def delete(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return render_to_json_response({
                'status': 'fail',
                'message': 'Not authenticated',
            })
        video_id = kwargs.get('video_id', None)
        if video_id is not None:
                self.request.user.userprofile.favorite_videos.remove(video_id)
                return render_to_json_response({
                    'status': 'ok',
                })
        else:
            return render_to_json_response({
                'status': 'fail',
                'message': 'Does not exist',
            })


class WatchLaterView(View):
    def delete(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return render_to_json_response({
                'status': 'fail',
                'message': 'Not authenticated',
            })
        video_id = kwargs.get('video_id', None)
        if video_id is not None:
                self.request.user.userprofile.watch_later_videos.remove(
                    video_id)
                return render_to_json_response({
                    'status': 'ok',
                })
        else:
            return render_to_json_response({
                'status': 'fail',
                'message': 'Does not exist',
            })


@login_required
def get_watch_later(request, page_number):
    if request.method != "GET":
        return HttpResponseBadRequest()
    profile = request.user.userprofile
    page = _paginate_video_set(profile.watch_later_videos.all(),
                               page_number)
    if request.is_ajax():
        return HttpResponse(
            _build_response(page),
            content_type='application/json')
    else:
        if page is None:
            raise Http404
        return render_to_response(
            'distance_learning/profile.html',
            {'videos': page,
             'result_type': 'watch-later',
             'pages': range(page.paginator.num_pages)},
            context_instance=RequestContext(request))


@permission_required('distance_learning.add_video', raise_exception=True)
def get_uploaded(request, page_number):
    if request.method != "GET":
        return HttpResponseBadRequest()
    page = _paginate_video_set(
        request.user.video_set.all().filter(approved=True),
        page_number)
    if request.is_ajax():
        return HttpResponse(
            _build_response(page),
            content_type='application/json')
    else:
        if page is None:
            raise Http404
        return render_to_response(
            'distance_learning/profile.html',
            {'videos': page,
             'result_type': 'uploaded',
             'pages': range(page.paginator.num_pages)},
            context_instance=RequestContext(request))


@login_required
def profile(request):
    """
    A view rendering a user's profile.
    """
    return redirect('profile-get-favorites', page_number=1)


class ProfileSettingsView(UpdateView):
    """
    A view allowing a user to update their settings.
    """
    template_name = 'registration/profile_settings.html'
    success_url = reverse_lazy('profile-settings')

    def get_form_class(self):
        """
        Gets the appropriate form class for the type of the Member object
        associated with the currently logged in user.
        """
        return get_form_for_model(type(self.get_object()))

    def get_object(self):
        """
        Gets the Member object associated with the currently logged in user
        """
        if not hasattr(self, 'object') or self.object is None:
            self.object = self.request.user.userprofile.member.cast()
        return self.object

    def form_valid(self, form):
        SUCCESS_MESSAGE = 'Your profile was updated successfully.'
        if self.request.is_ajax():
            form.save()
            return render_to_json_response({
                'status': 'ok',
                'message': SUCCESS_MESSAGE
            })
        else:
            messages.success(self.request, SUCCESS_MESSAGE)
            return super(ProfileSettingsView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return render_to_json_response({
                'status': 'validation failed',
                'errors': form.errors
            })
        else:
            return super(ProfileSettingsView, self).form_invalid(form)

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            return render_to_response(
                    'registration/profile_form.html',
                    {'form': self.get_form(self.get_form_class()),
                     'submit_view_name': 'profile-settings'},
                    context_instance=RequestContext(self.request))
        else:
            return super(ProfileSettingsView, self).get(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileSettingsView, self).dispatch(*args, **kwargs)
