from django.db import models
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.dispatch import receiver
from django.template.loader import render_to_string

from distance_learning.models import Video

from accounts.utils import get_or_none
from common.utils import generate_random_string

from common.utils import send_mail

from emailconfirmation.signals import email_confirmed


# TODO: It could be a good idea to create a custom model.Manager which
# would always do select_related queries, forcing the database to return
# data for the subclasses immediately => less queries hitting the DB.
class Member(models.Model):
    """
    A base model class for all users who can be registered on the website.
    Subclasses define additional attributes relevant for them, whereas
    here only the basic and necessary attributes are defined.
    """
    # These fields are not stored in the database for the Member object,
    # but rather in the user profile
    _username = None
    _password = None
    _group_name = None
    _active = None

    # We use properties for these fields which is the pythonic way
    # of implementing getters/setters.  It also alows subclasses to use
    # username and password as key word arguments in their constructors
    @property
    def username(self):
        """
        The getter for the username property.
        """
        if self._username is not None:
            return self._username
        # Try to get a username from the userprofile
        try:
            self._username = self.userprofile.user.username
        except UserProfile.DoesNotExist:
            # User profile does not exist
            return None
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        # Check if this is already linked with an object in the database.
        # If it is, change the username in the user account too.
        try:
            self.userprofile.user.username = value
        except UserProfile.DoesNotExist:
            pass

    @property
    def password(self):
        """
        A getter for the password property.  The value it returns may not
        be the actual password for the user, but a hash value.
        """
        if self._password is not None:
            return self._password
        try:
            self._password = self.userprofile.user.username
        except UserProfile.DoesNotExist:
            # User profile does not exist
            return None
        return self._username

    @password.setter
    def password(self, value):
        self._password = value
        try:
            self.userprofile.user.set_password(value)
            self._password = self.userprofile.user.password
        except UserProfile.DoesNotExist:
            pass

    @property
    def group_name(self):
        return self._group_name

    @group_name.setter
    def group_name(self, value):
        self._group_name = value

    @property
    def active(self):
        """
        The getter for the active property.
        """
        if self._active is not None:
            return self._active
        # Try to get it from the userprofile
        try:
            self._active = self.userprofile.user.is_active
        except UserProfile.DoesNotExist:
            # User profile does not exist.
            # The default value for active is False.
            self._active = False
        return self._active

    @active.setter
    def active(self, value):
        """
        The setter for the active property.
        """
        self._active = value
        # Check if this is already linked with an object in the database.
        # If it is, change the username in the user account too.
        try:
            self.userprofile.user.is_active = value
        except UserProfile.DoesNotExist:
            pass

    def can_upload_video(self):
        """
        Returns a boolean indicating whether the Member is allowed to
        upload videos.
        """
        return self.userprofile.user.has_perm('distance_learning.add_video')

    # Holds the reference to the child object of the particular Member
    _subobject = None

    def _register(self, user=None):
        """
        The method registers the member to the website.  This entails
        creating a user account and a user profile linked to the Member
        object.  The models which inherit from Member can thus be reached
        through a user account/profile.
        The keyword argument `user` represents an existing auth.User object to
        use for the Member instance instead of creating a new one.
        """
        if user is None:
            user = User.objects.create_user(
                username=self.username,
                password=self.password)
        user.is_active = self.active
        # Automatically add the user to the proper group
        if self._group_name is not None:
            group = get_or_none(Group, name=self._group_name)
            if group is not None:
                user.groups.add(group)

        user.save()
        profile = UserProfile(user=user, member=self)
        profile.save()

    _subclass_fields = None

    @property
    def subclass_fields(self):
        """
        The property returns all field names which could are fields to
        access the subclass object of the base model class Member.
        """
        if self._subclass_fields is None:
            # Introspection to find the fields
            self._subclass_fields = [
                att
                for att in dir(self.__class__)
                if (isinstance(getattr(self.__class__, att),
                               SingleRelatedObjectDescriptor) and
                    issubclass(getattr(self.__class__, att).related.model,
                               self.__class__))]
        return self._subclass_fields

    def save(self, *args, **kwargs):
        """
        Overrides the builtin save method to create and save a user account
        for each Member object saved.
        """
        create = self.id is None
        # Strip out the user keyword argument, since the super save method
        # does not expect it.
        user = None
        if 'user' in kwargs:
            user = kwargs.pop('user')
        super(Member, self).save(*args, **kwargs)
        # Only register if the object is not being updated
        if create:
            self._register(user=user)
        else:
            # User and UserProfile already exist so save them too
            self.userprofile.save()
            self.userprofile.user.save()

    def delete(self, *args, **kwargs):
        """
        Overrides the builtin delete method to delete the user account
        associated with each Member object.
        """
        # Delete the User and UserProfile objects associated with the
        # Member.
        user_profile = self.userprofile
        user = user_profile.user
        user_profile.delete()
        user.delete()
        # Delete the member itself
        super(Member, self).delete(*args, **kwargs)

    def deactivate(self):
        """
        The function deactivates the user account for the Member,
        effectively disallowing access to all private functionality.
        It is preferred to use this method instead of outright
        deleting the Member.
        """
        self.active = False

    def confirm_email(self):
        """
        A method which should be called once the member has confirmed the
        email
        """
        # The base class' implementation does nothing
        pass

    def cast(self):
        """
        The method casts the Member object to the subclass object for which
        it is the base object.
        """
        # If the method has already been called
        if self._subobject is not None:
            return self._subobject
        for field in self.subclass_fields:
            try:
                self._subobject = getattr(self, field)
                # If an exception is not thrown, we've found the subclass
                break
            except self.DoesNotExist:
                pass
        # If no child is found, it returns None.
        return self._subobject

    _video_set = None
    @property
    def video_set(self):
        """
        Returns a QuerySet with all videos related to the Member object.
        A Member is related to a video if he submitted the Video.
        """
        # Just proxies the User's video_set
        if self._video_set is None:
            self._video_set = self.userprofile.user.video_set
        return self._video_set

    def __unicode__(self):
        return u'%s' % self.username

    def __str__(self):
        return '%s' % self.username

    @models.permalink
    def get_admin_url(self):
        return ('admin:accounts_member_change', (self.id,), {})


class Student(Member):
    """
    A Member subclass defining attributes for a Student member.
    """
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    email = models.EmailField()
    country = models.CharField(max_length=55, blank=True)
    city = models.CharField(max_length=60, blank=True)
    eestec_member = models.BooleanField(default=False,
                                        verbose_name='EESTEC member')

    @models.permalink
    def get_admin_url(self):
        return ('admin:accounts_student_change', (self.id,), {})

    def __init__(self, *args, **kwargs):
        self.group_name = 'Students'
        super(Student, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s %s' % (self.name, self.surname)

    def confirm_email(self):
        """
        Overrides the base confirm_email method to activate the Individual's
        account.
        """
        self.active = True
        self.save()


class Company(Member):
    """
    A Member subclass defining attributes for a Company member.
    """
    name = models.CharField(max_length=150)
    email = models.EmailField()
    country = models.CharField(max_length=55, blank=True)
    city = models.CharField(max_length=60, blank=True)
    address = models.CharField(max_length=100, blank=True)

    @models.permalink
    def get_admin_url(self):
        return ('admin:accounts_company_change', (self.id,), {})

    def __init__(self, *args, **kwargs):
        self.group_name = 'Companies'
        super(Company, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name_plural = "companies"


class University(Member):
    """
    A Member subclass defining attributes for a University member.
    """
    name_of_university = models.CharField(max_length=100)
    name_of_faculty = models.CharField(max_length=100)
    email = models.EmailField()
    country = models.CharField(max_length=55, blank=True)
    city = models.CharField(max_length=60, blank=True)
    address = models.CharField(max_length=100, blank=True)

    @models.permalink
    def get_admin_url(self):
        return ('admin:accounts_university_change', (self.id,), {})

    def __init__(self, *args, **kwargs):
        self.group_name = 'Universities'
        super(University, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s, %s' % (self.name_of_university, self.name_of_faculty)

    class Meta:
        verbose_name_plural = "universities"


class LocalCommittee(Member):
    """
    A Member sublcass defining attributes for EESTEC LC member accounts.
    """
    city = models.CharField(max_length=60)
    email = models.EmailField()
    country = models.CharField(max_length=55, blank=True)

    @models.permalink
    def get_admin_url(self):
        return ('admin:accounts_localcommittee_change', (self.id,), {})

    def __init__(self, *args, **kwargs):
        self.group_name = 'LCs'
        super(LocalCommittee, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'LC %s' % (self.city)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to provide a default username and a random
        password to LCs which are emailed to the provided email address.
        """
        create = self.id is None
        if create:
            self.username = u'lc_' + self.city.lower()
            # Give the user a randomly generated password
            password = generate_random_string()
            self.password = password
            # Compose the email to send to the LC
            context = {
                'lc': self,
                'password': password,
            }
            subject = render_to_string(
                'registration/lc_register_email_subject.txt')
            subject = subject.strip()
            message = render_to_string(
                'registration/lc_register_email_text.txt',
                context)
            send_mail(subject,
                      message,
                      settings.DEFAULT_FROM_EMAIL,
                      [self.email])
        # Delegate upward to the parent classes
        super(LocalCommittee, self).save(*args, **kwargs)


class UserProfile(models.Model):
    """
    A model describing a user profile.  User profiles attach additional
    information to a django User model.  Here, a reference to a Member
    object is held thus enabling access to a particular Member subclass
    directly from the User.
    """
    user = models.OneToOneField(User)
    member = models.OneToOneField(Member)
    favorite_videos = models.ManyToManyField(
        Video,
        related_name="%(class)s_favorite_set")
    watch_later_videos = models.ManyToManyField(
        Video,
        related_name="%(class)s_watch_later_set")


@receiver(email_confirmed)
def handle_email_confirmed(sender, **kwargs):
    """
    A receiver callback which handles the email_confirmed signal raised by
    the emailconfirmation app.
    It makes sure that after a user confirms the email, is turned into an
    active user.
    """
    email = kwargs['email_address']
    email.user.userprofile.member.cast().confirm_email()
