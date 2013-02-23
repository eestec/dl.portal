"""
Distance Learning application views.
"""
from django.template import RequestContext
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import permission_required, login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from django.utils import simplejson
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from distance_learning.models import Video
from distance_learning.forms import VideoUploadForm
from distance_learning.forms import VideoSearchForm
from distance_learning.forms import CommentPostForm
from distance_learning.utils import get_or_none
from distance_learning.uploadhandlers import QuotaUploadHandler

from haystack.query import SearchQuerySet, AutoQuery, SQ

import urllib


def index(request):
    """
    A view for the index page.  It needs to fetch most popular
    content which is to be rendered in the template.
    """
    # TODO: Get most popular videos
    videos = Video.objects.get_most_viewed()
    return render_to_response('distance_learning/index.html',
                              {'videos': videos},
                              context_instance=RequestContext(request))


@permission_required('distance_learning.add_video', raise_exception=True)
@csrf_exempt
def upload_video(request):
    """
    A view for uploading a new video to the website.
    """
    # Add a QuotaHandler to stop possible DoS by uploading huge files
    # Because an UploadHandler is being dynamically added, it must be done
    # before reading any POST data.  This is why the view is csrf_exempt,
    # since the csrf check reads POST.
    # The helper private function is csrf_protected to eventually check
    # the csrf token.
    # TODO: Maybe make a view decorator which adds the QuotaUploadHandler
    # thereby making the splitting of methods unnecessary.
    request.upload_handlers.insert(0, QuotaUploadHandler())
    return _upload_video(request)


@csrf_protect
def _upload_video(request):
    """
    A private helper function for the upload_video view which checks for
    csrf since upload_view must not read any data before setting the
    UploadHandler
    """
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Do not commit!
                # The view needs to inject the user who uploaded the vid
                video = form.save(commit=False)
                video.user = request.user
                video.save()
                # When calling the save method with commit=False, Django
                # adds a save_m2m method to the form object when m2m fields
                # exist in the model.  We need to call it manually to save
                # the m2m links.
                form.save_m2m()
            except IntegrityError:
                # TODO: Redirect to a failure page...
                pass
            # TODO: Redirect to a proper success page
            return HttpResponseRedirect('/')
    else:
        # TODO: Maybe populate the form with some defaults which can be
        # gathered from the user trying to upload the video (city, country)
        form = VideoUploadForm()
    return render_to_response(
        'distance_learning/upload.html',
        {'form': form},
        context_instance=RequestContext(request))


def show_video(request, video_id):
    """
    A view which renders the video whose id is provided as a parameter.
    """
    video = get_object_or_404(Video, pk=video_id)
    if not video.approved:
        raise Http404
    # Only render the form if the user is allowed to submit comments to the
    # video.
    comment_form = None
    if request.user is not None:
        if request.user.has_perm('distance_learning.add_comment'):
            comment_form = CommentPostForm()
    return render_to_response(
        'distance_learning/video.html',
        {'video': video,
         'comment_form': comment_form},
        context_instance=RequestContext(request))


def search(request, **kwargs):
    """
    The view for showing search results and processing search queries.
    """
    # TODO: Render a different template for AJAX requests
    if len(request.GET) != 0:
        # Fetch videos only if a search form was submitted
        form = VideoSearchForm(request.GET)
        if form.is_valid():
            videos = form.get_query_set()
            return render_to_response(
                'distance_learning/search.html',
                {'form': form,
                 'videos': videos},
                context_instance=RequestContext(request))
        else:
            # Belaj
            pass
    else:
        form = VideoSearchForm()

    return render_to_response(
        'distance_learning/search.html',
        {'form': form},
        context_instance=RequestContext(request))


def live_broadcast(request):
    """
    A view which renders the live broadcast page.
    """
    videos = Video.objects.all_active_broadcast()
    if videos:
        # For now, we'll allow only one live broadcast to be shown at a time
        video = videos[0]
    else:
        # No videos are flaged as an active live broadcast event
        return render(request, 'distance_learning/live.html', {
            'videos': None,
        })
    return redirect(video)


@permission_required('distance_learning.add_comment', raise_exception=True)
def post_comment(request, video_id):
    """
    A view which saves the comment on the video with the given id.
    """
    # TODO: AJAX-specific response
    if request.method == 'POST':
        form = CommentPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.video = get_object_or_404(Video, pk=video_id)
            post.user = request.user
            post.save()
        # Redirect back to the video page - thereby refreshing the page
        # and showing the new comment
        return HttpResponseRedirect(
            reverse('distance_learning.views.show_video',
                    args=(video_id,)))
    return Http404


def video_search_json(request):
    """
    A view which returns a JSON list of video names matching the search query.
    """
    if 'q' not in request.GET:
        return HttpResponse('',
                            content_type='application/json')
    videos = SearchQuerySet().filter(SQ(content=AutoQuery(request.GET['q'])) |
                                     SQ(name=AutoQuery(request.GET['q'])))
    return HttpResponse(simplejson.dumps([video.name for video in videos]),
                        content_type='application/json')


def video_autocomplete_search(request):
    """
    A view which returns a JSON list of videos matching the search query where
    the search works in an autocomplete way.
    """
    if 'q' not in request.GET:
        return HttpResponse('',
                            content_type='application/json')
    videos = SearchQuerySet().autocomplete(content_auto=request.GET['q'])
    return HttpResponse(simplejson.dumps([video.name for video in videos]),
                        content_type='application/json')


def _paginate_video_set(query_set, page_number=1):
    VIDEOS_PER_PAGE = 6
    paginator = Paginator(query_set, VIDEOS_PER_PAGE)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = None
    return page


def video_search(request):
    """
    A view which shows videos matching a search query.
    """
    q = request.GET.get('q', '')
    videos = SearchQuerySet().filter(content_auto=AutoQuery(q))
    videos = tuple(sorted((video.object for video in videos),
                          key=lambda v: -v.views))
    page_number = request.GET.get('page', 1)
    page = _paginate_video_set(videos,
                               page_number=page_number)
    return render_to_response(
        'distance_learning/video_list.html', {
            'videos': page,
            'page_links': (urllib.urlencode({'q': q, 'page': p + 1})
                           for p in range(page.paginator.num_pages)),
        },
        context_instance=RequestContext(request))


def all_videos(request):
    """
    A view which renders all videos on a page.
    """
    # TODO: Pagination.
    # Categorize them
    categorized_videos = {}
    for video in Video.objects.all_approved():
        if video.video_type not in categorized_videos:
            categorized_videos[video.video_type] = []
        categorized_videos[video.video_type].append(video)
    return render_to_response(
        'distance_learning/all_videos.html',
        {'videos': Video.objects.filter(approved=True),
         'categorized_videos': categorized_videos},
        context_instance=RequestContext(request))


def most_viewed_videos(request):
    """
    A view returning a JSON encoded list of the most viewed videos.
    """
    return HttpResponse(
        simplejson.dumps(
            [video.to_dict() for video in Video.objects.get_most_viewed()]),
        content_type='application/json')


def recent_videos(request):
    """
    A view returning a JSON encoded list of the most recent videos.
    """
    return HttpResponse(
        simplejson.dumps(
            [video.to_dict() for video in Video.objects.get_recent()]),
        content_type='application/json')
