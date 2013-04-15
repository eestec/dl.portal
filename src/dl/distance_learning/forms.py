from __future__ import division
from django import forms
from django.forms import ModelForm
from django.forms.models import fields_for_model
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from django.db.models import Q

from distance_learning.models import Video
from distance_learning.models import Comment


class VideoUploadForm(ModelForm):
    class Meta:
        model = Video
        # The approved and active_broadcast flags are excluded from the form
        # shown to the user.
        # They default to False and only the admin can change them to True
        # The upcoming and preview_image fields are also excluded since
        # they are ignored for videos which are not considered upcoming.
        exclude = (
            'approved',
            'active_broadcast',
            'upcoming',
            'preview_image',
        )

    def __init__(self, *args, **kwargs):
        super(VideoUploadForm, self).__init__(*args, **kwargs)
        self.fields['video_url'].required = True

    def save(self,
             force_insert=False, force_update=False, commit=True,
             *args, **kwargs):
        v = super(VideoUploadForm, self).save(commit=False)
        v.upcoming = False
        if commit:
            v.save()
        return v


class UpcomingVideoUploadForm(ModelForm):
    class Meta:
        model = Video
        exclude = (
            'approved',
            'active_broadcast',
            'live_broadcast',
            'upcoming',
        )

    def __init__(self, *args, **kwargs):
        super(UpcomingVideoUploadForm, self).__init__(*args, **kwargs)
        self.fields['video_url'].label = u'Link to a promotional video'
        self.fields['preview_image'].help_text = (
            u'Aspect ratio of the image needs to be 4:3'
        )

    def clean_preview_image(self):
        """
        A custom field validator ensuring the aspect ratio of the uploaded
        image is 4:3.
        """
        preview_image = self.cleaned_data['preview_image']
        if preview_image:
            width, height = get_image_dimensions(preview_image)
            aspect_ratio = width / height
            if aspect_ratio != 4 / 3:
                raise forms.ValidationError(
                    u'The aspect ratio of the image needs to be 4:3.')
        return preview_image

    def clean(self):
        """
        A custom clean method to cross validate fields.
        The form is valid only if at least one of video_url or
        preview_image is set.
        """
        cleaned_data = super(UpcomingVideoUploadForm, self).clean()
        # A promo video or a preview image must be set
        video_url = cleaned_data.get('video_url')
        preview_image = cleaned_data.get('preview_image')
        if not (video_url or preview_image):
            raise forms.ValidationError(
                'A promotional video or a preview image must be set.')

        return cleaned_data

    def save(self,
             force_insert=False, force_update=False, commit=True,
             *args, **kwargs):
        """
        A custom save method for the form which sets field values specific for
        UpcomingVideos.
        """
        v = super(UpcomingVideoUploadForm, self).save(commit=False, 
                                                      *args, **kwargs)
        v.upcoming = True
        if commit:
            v.save()
        return v


class CommentPostForm(ModelForm):
    """
    A ModelForm for the Post model.  The form's client must make sure to set
    the video and user fields of the model based on the context in which the
    Post is being created/submitted.
    """
    class Meta:
        model = Comment
        exclude = (
            'video',
            'user',
        )


class VideoSearchForm(forms.Form):
    """
    A form class which allows the user to get search results based on
    form fields for a particular model.  It is also possible to add
    extra fields for custom processing.
    Following the YAGNI prinicple, it is only implemented for the Video
    model, instead of being an overly generic solution for all models.
    If the need for a different search appears, it can be refactored to
    have a greater level of abstraction.
    """
    # Fields to be excluded from the search.  They will in no way influence
    # search results
    exclude_fields = (
        'approved',
        'active_broadcast',
        'video_url',
        'description',
        'handout',
        'presentation',
    )
    # Fields to be tested for equality with the search term entered.  Only
    # if the value of the field is the same in the Video object will it be
    # returned in the result
    test_equal = set((
        'video_type',
        'subject',
    ))
    field_order_priority = (
        'name',
    )

    def __init__(self, *args, **kwargs):
        super(VideoSearchForm, self).__init__(*args, **kwargs)
        # Get all fields for the Video model, except the ones which are to
        # be excluded
        self.fields.update(dict(
            (field_name, form_field)
            for field_name, form_field
            in fields_for_model(Video).iteritems()
            if field_name not in self.exclude_fields))

        # None of the fields in the search form are required
        for name, field in self.fields.iteritems():
            field.required = False

        self._set_field_ordering()

    def _set_field_ordering(self):
        """
        A private helper method to factor out the setting of proper field order
        for the form.
        It uses the tuple field_order_priority and places the fields from the
        tuple in the beginning of the form in the specified order.  Other
        fields do not have a guarantee as for their position in the form.
        """
        # Set some field ordering
        for field in reversed(self.field_order_priority):
            # Remove the field and place it back in the beginning of the list
            # As the order tuple is traversed in reversed order, the first
            # member of the tuple will be left in the beginning of the ordering
            # list.
            self.fields.keyOrder.remove(field)
            self.fields.keyOrder.insert(0, field)

    def get_query_set(self):
        """
        The method executes a search query based on the form data and
        settings returning a QuerySet for the Video model.
        """
        # Construct the options for the filter() method of the Manager
        qs = Video.objects.all()
        for name, data in self.cleaned_data.iteritems():
            if name == 'q': continue
            if name in self.test_equal:
                if data:
                    qs = qs.filter(**{name: data})
            else:
                for part in data.split():
                    qs = qs.filter(**{name + '__icontains': part})
        return qs
