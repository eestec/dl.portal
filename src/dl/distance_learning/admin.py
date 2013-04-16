from django.contrib import admin
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from distance_learning.models import Video
from distance_learning.models import VideoType
from distance_learning.models import VideoSubject


class AdminVideoUploadForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminVideoUploadForm, self).__init__(*args, **kwargs)
        self.fields['keywords'].widget = \
            admin.widgets.AdminTextInputWidget()

    class Meta:
        model = Video


class VideoAdmin(admin.ModelAdmin):
    form = AdminVideoUploadForm
    list_display = (
            'name',
            'city',
            'event',
            'date_uploaded',
            'approved',
            'live_broadcast',
            'active_broadcast',
            'upcoming',
    )
    list_filter = (
            'date_uploaded',
            'approved',
            'live_broadcast',
            'upcoming',
    )

    def save_model(self, request, obj, form, change):
        """
        Overrides the base save_model so that if a video object is created
        through the admin interface, the user associated with the video
        is the admin.
        """
        if not change:
            obj.user = request.user
        obj.save()


admin.site.register(Video, VideoAdmin)
# Allow the admin to add subjects and types...
admin.site.register(VideoSubject)
admin.site.register(VideoType)
