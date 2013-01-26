from django import forms
from django.forms import ModelForm
from django.forms.models import fields_for_model

from django.db.models import Q

from distance_learning.models import Video
from distance_learning.models import Comment


class VideoUploadForm(ModelForm):
    class Meta:
        model = Video
        # The approved flag is excluded from the form shown to the user.
        # It defaults to False and only the admin can change it to True
        exclude = (
            'approved',
        )


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
