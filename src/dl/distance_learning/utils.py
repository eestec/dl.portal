from django.db import models
from django.db.models import FileField
from django.forms import ValidationError
from django.template.defaultfilters import filesizeformat
from django import forms 

from admin_notifications.models import AdminNotification

class PrettyPrintList(object):
    """
    A class which wraps the builtin list object so that when it is
    converted to a string, it is printed as a comma delimited list of
    its contents.
    >>> a = PrettyPrintList([1, 2, 3])
    >>> print a
    1, 2, 3
    >>> print PrettyPrintList([u'one', u'2', u'3'])
    one, 2, 3
    >>> a == [1, 2, 3]
    True
    >>> a == ['1', '2', '3']
    False
    >>> a == a
    True
    >>> print a.__unicode__()
    1, 2, 3
    """
    def __eq__(self, rhs):
        if isinstance(rhs, PrettyPrintList):
            return self._list == rhs._list
        return self._list == rhs

    def __init__(self, l):
        self._list = l
    def __iter__(self):
        """
        Method implemented so that this class is also iterable like
        the list it wraps.  The method simply calls the list's method.
        """
        return self._list.__iter__()
    def next(self):
        """
        Method implemented so that this class is also iterable like
        the list it wraps.  The method simply calls the list's method.
        """
        return self._list.next()
    def __getitem__(self, pos):
        """
        Makes the objects of this class indexable, like the list
        itself.
        """
        return self._list.__getitem__(pos)
    def __str__(self):
        """
        The method converts the list into a comma delimited string
        of its contents.
        """
        return ', '.join([str(i) for i in self._list])
    def __unicode__(self):
        """
        The method converts the list into a comma delimited string
        of its contents.
        """
        return ', '.join(
                [i if isinstance(i, unicode) else unicode(i) 
                    for i in self._list])
class CommaDelimitedTextField(models.TextField):
    """
    A custom model Field for storing a comma delimited list of strings.
    It extends the TextField model field class.
    """
    __metaclass__ = models.SubfieldBase
    description = "Stores a comma delimited list of strings"
    def __init__(self, *args, **kwargs):
        super(CommaDelimitedTextField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Returns a python object which is created by the data in the `value`.
        The object returned is an instance of the `PrettyPrintList` class.
        """
        if value is None:
            return None

        if isinstance(value, PrettyPrintList):
            return value

        # All white space after commas is ignored
        return PrettyPrintList([i.strip() for i in value.split(',')])

    def get_prep_value(self, value, **kwargs):
        if value is None:
            return
        # Sanity check
        assert isinstance(value, PrettyPrintList)

        return ','.join(value)

    def get_db_prep_value(self, value, **kwargs):
        return self.get_prep_value(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def formfield(self, **kwargs):
        """
        Overrides the base class's method to have a TextInput instead of
        a Textarea as a default
        """
        defaults = {'widget': forms.TextInput}
        defaults.update(kwargs)
        return super(CommaDelimitedTextField, self).formfield(**defaults)
        

class LimitedFileField(FileField):
    """
    Extends FileField to disallow upload of files larger than
    max_upload_size
    """

    def __init__(self, *args, **kwargs):
        self.max_upload_size = kwargs.pop("max_upload_size")

        super(LimitedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """
        Transform and validate the field's data
        """
        data = super(LimitedFileField, self).clean(*args, **kwargs)
        file = data.file

        if file.size > self.max_upload_size:
            raise ValidationError(
                    "File size exceeds %s" % filesizeformat(self.max_upload_size))
        return data


def send_admin_notification(message, handle_url):
    notification = AdminNotification(message=message,
                                     handle_url=handle_url,
                                     app_name='distance_learning')
    notification.save()


def get_or_none(model, **kwargs):
    """
    Gets a Django Model object from the database or returns None if it
    does not exist.
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def add_url_to_context(request):
    """
    Context processor which adds the full path to the current page to the
    context.
    """
    return {
        'full_path': request.build_absolute_uri(request.path)
    }
