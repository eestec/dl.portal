from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView

from hitcount.views import update_hit_count_ajax

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
)

# Admin notification mappings
urlpatterns += patterns('',
    url(r'^admin/notification/all$',
        'admin_notifications.views.show_all_notifications',
        name='admin-notifications-all'),
    url(r'^admin/notification/delete/(?P<notification_id>\d+)/$',
        'admin_notifications.views.dismiss_notification',
        name='admin-notifications-delete'),
)

# Account related url mappings
# TODO: Move to an accounts/urls file
from accounts.views import ProfileSettingsView, FavoritesView, WatchLaterView
urlpatterns += patterns('',
    url(r'^accounts/login/$',
        'accounts.views.custom_login',
        name='user-login'), 
    url(r'^accounts/logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='user-logout'),
    url(r'^accounts/register/individual/$',
        'accounts.views.register_student',
        name='register-student'),
    url(r'^accounts/register/university/$',
        'accounts.views.register_university',
        name='register-university'),
    url(r'^accounts/register/company/$',
        'accounts.views.register_company',
        name='register-company'),
    url(r'^accounts/register/success/$',
        TemplateView.as_view(
            template_name='registration/success-register.html'),
        name='register-success'),
    url(r'^accounts/profile/favorites/$',
        'accounts.views.add_favorite',
        name='profile-add-favorite'),
    url(r'^accounts/profile/favorites/video/(?P<video_id>\d+)/$',
        FavoritesView.as_view(),
        name='profile-favorite'),
    url(r'^accounts/profile/favorites/(?P<page_number>\d+)/$',
        'accounts.views.get_favorites',
        name='profile-get-favorites'),
    url(r'^accounts/profile/watch-later/$',
        'accounts.views.add_watch_later',
        name='profile-add-watch-later'),
    url(r'^accounts/profile/watch-later/video/(?P<video_id>\d+)/$',
        WatchLaterView.as_view(),
        name='profile-watch-later'),
    url(r'^accounts/profile/watch-later/(?P<page_number>\d+)/$',
        'accounts.views.get_watch_later',
        name='profile-get-watch-later'),
    url(r'^accounts/profile/uploaded/(?P<page_number>\d+)/$',
        'accounts.views.get_uploaded',
        name='profile-get-uploaded'),
    url(r'^accounts/profile/$',
        'accounts.views.profile',
        name='dl-profile'),
    url(r'^accounts/profile/settings/$',
        ProfileSettingsView.as_view(),
        name='profile-settings'),
)

# Distance learning mappings
# TODO: Move to a distance_learning/urls file
from contact.views import BugReportCreate
urlpatterns += patterns('',
    url(r'^$',
        'distance_learning.views.index',
        name='dl-index'),
    url(r'^live/$',
        'distance_learning.views.live_broadcast',
        name='dl-live'),
    url(r'^video/upload/$',
        'distance_learning.views.upload_video',
        {'video_type': 'video'},
        name='dl-video-upload'),
    url(r'^video/upload-upcoming/$',
        'distance_learning.views.upload_video',
        {'video_type': 'upcoming'},
        name='dl-video-upcoming-upload'),
    url(r'^video/(?P<video_id>\d+)/update/$',
        'distance_learning.views.update_video',
        name='dl-video-update'),
    url(r'^video/(?P<video_id>\d+)/update-existing/$',
        'distance_learning.views.update_video',
        {'video_type': 'existing'},
        name='dl-video-update-existing'),
    url(r'^video/(?P<video_id>\d+)/update-upcoming/$',
        'distance_learning.views.update_video',
        {'video_type': 'upcoming'},
        name='dl-video-update-upcoming'),
    url(r'^browse/$',
        'distance_learning.views.browse',
        name='dl-browse'),
    url(r'^browse/video/recent/$',
        'distance_learning.views.recent_videos',
        name='dl-video-recent'),
    url(r'^browse/video/most-viewed/$',
        'distance_learning.views.most_viewed_videos',
        name='dl-video-most-viewed'),
    url(r'^browse/video/category/(?P<category_name>[a-zA-Z]+)/$',
        'distance_learning.views.category_search',
        name='dl-video-category-search'),
    url(r'^browse/video/category/(?P<category_name>[a-zA-Z]+)/(?P<subcategory_id>[0-9a-zA-Z]+)/$',
        'distance_learning.views.subcategory_search',
        name='dl-video-subcategory-search'),

    url(r'^video/(?P<video_id>\d+)/$',
        'distance_learning.views.show_video',
        name='dl-video-show'),

    url(r'^video/(?P<video_id>\d+)/comment/upload/$',
        'distance_learning.views.post_comment',
        name='dl-post-comment'),

    url(r'^video/search/$',
        'distance_learning.views.video_search',
        name='dl-video-search'),
    # JSON end points
    url(r'^api/video/search/$',
        'distance_learning.views.video_search_json',
        name='dl-video-search-json'),
    url(r'^api/video/search/autocomplete/$',
        'distance_learning.views.video_autocomplete_search',
        name='dl-video-autocomplete-json'),
    url(r'^api/video/recent/$',
        'distance_learning.views.recent_videos_json',
        name='dl-video-recent-json'),
    url(r'^api/video/most-viewed/$',
        'distance_learning.views.most_viewed_videos_json',
        name='dl-video-most-viewed-json'),
    url(r'^api/video/category/(?P<category_name>[a-zA-Z]+)/$',
        'distance_learning.views.category_search_json',
        name='dl-video-category-search-json'),
    url(r'^api/video/category/(?P<category_name>[a-zA-Z]+)/(?P<subcategory_id>[0-9a-zA-Z]+)/$',
        'distance_learning.views.subcategory_search_json',
        name='dl-video-subcategory-search-json'),
    # Flatpages-like pages
    url(r'^about/$',
        TemplateView.as_view(template_name="distance_learning/about.html"),
        name="dl-about"),
    url(r'^about/faq/$',
        TemplateView.as_view(template_name='distance_learning/faq-about.html'),
        name='dl-about-faq'),
    url(r'^about/eestec/$',
        TemplateView.as_view(
            template_name='distance_learning/eestec-about.html'),
        name='dl-about-eestec'),
    url(r'^about/contact/$',
        TemplateView.as_view(
            template_name='distance_learning/contact-about.html'),
        name='dl-about-contact'),
    url(r'^success/report/$',
        TemplateView.as_view(
            template_name='distance_learning/success-report.html'),
        name='dl-report-success'),
    url(r'^about/report/$',
        BugReportCreate.as_view(),
        name='dl-about-report'),
)

# contrib.admin patterns
urlpatterns += patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

# Social auth patterns
urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),
)

# Hit counter patterns
urlpatterns += patterns('',
    url(r'^ajax/hit/$',
        update_hit_count_ajax,
        name='hitcount_update_ajax'),
)

# Email confirmation patterns
urlpatterns += patterns('',
    url(r'^confirm_email/(\w+)/$',
        'emailconfirmation.views.confirm_email',
        name='emailconfirmation_confirm_email'),
)

# Debug patterns
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
