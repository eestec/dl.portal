from django.forms import ModelForm
import django.forms
from accounts.models import Member, Student, University, Company
from accounts.models import LocalCommittee
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_username_unique(value):
    """
    A custom username validator.
    """
    if User.objects.filter(username=value).count():
        raise ValidationError(u"Username '%s' already exists" % value)


class MemberForm(ModelForm):
    """
    A base class for all member forms.  It makes sure that they all
    have fields for the username and password.  It also makes sure that
    the username and password are saved with the Member object.
    """
    username = django.forms.CharField()
    password = django.forms.CharField(widget=django.forms.PasswordInput)
    repeat_password = django.forms.CharField(widget=django.forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        """
        Custom initialization of the member form.
        """
        super(MemberForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            # The form is created for an existing instance -> object
            # is being modified
            # Set the form field for the username (it is not a field of the
            # Member model -- it's a property).
            self.fields['username'].initial = instance.username
            # Set readonly fields
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
            # The user may choose not to change the password
            self.fields['password'].required = False
            self.fields['repeat_password'].required = False

    def clean_username(self):
        """
        A method for custom clean operations on the username field.
        """
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            # If the object is being modified always return the original
            # username value to prevent any POST funny-business overriding
            # expected functionality (usernames cannot be changed!)
            return instance.username
        # If the object is new we need to check for username uniqueness
        value = self.cleaned_data['username']
        validate_username_unique(value)
        return value

    def clean_email(self):
        """
        A method for custom clean operations on the email field.
        """
        # Possibly refactor this to a more general method which would take a
        # parameter indicating which field to return if the instance exists.
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            return instance.email
        else:
            return self.cleaned_data['email']

    def clean(self):
        """
        A method for custom clean operations.
        Cross validates the password and repeat_password fields to make sure
        they match.
        """
        cleaned_data = super(MemberForm, self).clean()
        password = cleaned_data.get('password', None)
        repeat_password = cleaned_data.get('repeat_password', None)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if not password:
                if repeat_password:
                    raise django.forms.ValidationError(
                        u"Passwords do not match")
                cleaned_data['password'] = instance.password
                return cleaned_data
        if password != repeat_password:
            raise django.forms.ValidationError(u"Passwords do not match")
        return cleaned_data

    def save(self,
            force_insert=False, force_update=False, commit=True,
            *args, **kwargs):
        """
        A custom save method which injects the username and password
        attributes into the model object since they are not model Fields, only
        Form fields.
        """
        m = super(MemberForm, self).save(commit=False, *args, **kwargs)
        m.username = self.cleaned_data['username']
        m.password = self.cleaned_data['password']
        if commit:
            m.save()
        return m


def _form_class_factory(model_class):
    """
    A helper function to instantiate form classes derived from MemberForm
    base class with varying models.  It takes a model class object (not an
    instance) as its parameter.  It returns a class object (not an
    instance).
    """
    class FormClass(MemberForm):
        class Meta:
            model = model_class
    return FormClass


# A dict relating model classes to their respective form classes
_model_to_form = {}
# Register all the Member models in the dict
member_models = [Student, Company, University, LocalCommittee]
for member_model in member_models:
    _model_to_form[member_model] = _form_class_factory(member_model)
    

def get_form_for_model(model_class):
    """
    Returns a Form class for the given model class.
    """
    return _model_to_form.get(model_class, None)
