import urlparse
from collections import namedtuple

from django.db import models
from django.dispatch import receiver
from django.core import urlresolvers
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save

from distance_learning.utils import LimitedFileField
from distance_learning.utils import CommaDelimitedTextField
from distance_learning.utils import send_admin_notification

from hitcount.models import HitCount
from hitcount.models import ContentType


class VideoSubject(models.Model):
    """
    A simple model for video subjects.  The name of the subject is unique.
    """
    subject_name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return u'%s' % self.subject_name


class VideoType(models.Model):
    """
    A simple model for video type.  The name of the type is unique.
    """
    type_name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return u'%s' % self.type_name


class VideoManager(models.Manager):
    """
    A custom Manager for the `Video` model.
    """
    def all_approved(self):
        """
        Returns a QuerySet of approved videos.
        """
        return super(VideoManager, self).get_query_set().filter(approved=True)

    def all_active_broadcast(self):
        """
        Returns a QuerySet of Videos which are flaged as an active broadcast.
        """
        return self.all_approved().filter(active_broadcast=True)

    def get_most_viewed(self, limit=5):
        """
        Returns videos sorted by the number of its hits.
        It should return `limit` results.
        `limit` defaults to 3 results.
        """
        videos = self.all_approved()
        return sorted(videos, key=lambda v: v.views, reverse=True)[:limit]

    def get_recent(self, limit=5):
        """
        Returns the most recent videos.
        """
        return self.all_approved().order_by('-date_uploaded')[:limit]


def validate_video_url(value):
    """
    A Video URL validator.
    Raises an error if the URL isn't from a supported video sharing site.
    So far, only youtube videos are supported.
    """
    def youtube_validator(url_split):
        """
        A sub-validator for youtube videos.
        """
        if url_split.path != '/watch':
            raise ValidationError(
                'Invalid Youtube video URL - not a watch link')
        v = urlparse.parse_qs(url_split.query).get('v', None)
        if v is None:
            raise ValidationError(
                'Invalid Youtube video URL - no video ID found')

    SITES_ALLOWED = {
        'youtube.com': youtube_validator,
    }
    url_split = urlparse.urlsplit(value)
    if url_split.hostname is not None:
        hostname = url_split.hostname
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        if hostname not in SITES_ALLOWED:
            raise ValidationError(
                u"Hostname '%s' is not supported." % url_split.hostname)
        # Now do a site-specific validation step
        site_validator = SITES_ALLOWED[hostname]
        return site_validator(url_split)


class Video(models.Model):
    # Custom Manager
    objects = VideoManager()

    name = models.CharField(max_length=100, verbose_name="Video name")
    date_uploaded = models.DateTimeField(auto_now_add=True)
    # Date when the video was taken?
    city = models.CharField(max_length=60)
    country = models.CharField(max_length=55)
    event = models.CharField(max_length=50)
    description = models.TextField()
    video_url = models.URLField(verbose_name="Video URL",
                                validators=[validate_video_url, ])
    live_broadcast = models.BooleanField(default=False)
    lecturer = models.CharField(max_length=60)
    # TODO: Refactor the max_upload_sizes to some settings file constant
    handout = LimitedFileField(
        upload_to=lambda instance, filename: '/'.join([instance.name,
                                                       'handouts',
                                                       filename]),
        max_upload_size=15 * 1024 * 1024,
        blank=True)
    presentation = LimitedFileField(
        upload_to=lambda instance, filename: '/'.join([instance.name,
                                                       'presentations',
                                                       filename]),
        max_upload_size=15 * 1024 * 1024,
        blank=True)
    video_type = models.ForeignKey(VideoType)
    keywords = CommaDelimitedTextField(max_length=150)
    subject = models.ManyToManyField(VideoSubject)
    user = models.ForeignKey(User, editable=False)
    active_broadcast = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    _views = None

    @property
    def views(self):
        """
        The property returns the number of hits (views) a video object has had.
        """
        if self._views is not None:
            return self._views
        try:
            hc = HitCount.objects.get(
                content_type=ContentType.objects.get_for_model(Video),
                object_pk=self.pk)
        except HitCount.DoesNotExist:
            self._views = 0
        else:
            self._views = hc.hits
        return self._views

    def contains(self, term):
        """
        Temp. A method which checks whether a certain term appears as a part
        of any field of the video.  For now it does not discern between words
        and substrings.
        """
        term = term.lower()
        return (term in self.name.lower() or
                term in self.city.lower() or
                term in self.country.lower() or
                term in self.event.lower() or
                term in self.description.lower() or
                term in self.lecturer.lower() or
                term in unicode(self.video_type).lower() or
                term in unicode(self.keywords).lower())

    def __unicode__(self):
        return u'%s, %s' % (self.name, self.city)

    @models.permalink
    def get_absolute_url(self):
        return ('distance_learning.views.show_video', (self.id,), {})

    def embed_url(self):
        """
        Returns a youtube url which can be used to embed the video to the
        Web page.  Generated from the video_url field.
        Assumes that the videos are only youtube videos (not other providers).
        For that to work, this function would need to be updated.
        """
        YOUTUBE_EMBED_URL_PATTERN = (
            'http://www.youtube.com/embed/%(video_id)s')
        query_string = urlparse.urlparse(self.video_url).query
        v = urlparse.parse_qs(query_string).get('v', None)
        # Sanity check: all youtube videos must have the v param and only
        # one value for it.
        assert v is not None and len(v) == 1
        return YOUTUBE_EMBED_URL_PATTERN % {'video_id': v[0]}

    def embed_html(self, width=420, height=315):
        """
        The method returns HTML for embedding the video into a Web page.
        Keyword arguments width and height are the width and height of the
        embedded frame.
        The generated HTML is marked safe so as to avoid having templates
        escape it.
        """
        # So far only youtube videos are supported -- would need some
        # refactoring if it's decided to use different providers.
        YOUTUBE_VIDEO_EMBED_HTML_PATTERN = (
            """<iframe width="%(width)d" height="%(height)d" """
            """src="%(url)s%(params)s" frameborder="0" """
            """allowfullscreen></iframe>""")
        data = {
            'width': width,
            'height': height,
            'url': self.embed_url(),
            'params': '?wmode=transparent',      # Solved the overlap issue
        }
        return mark_safe(YOUTUBE_VIDEO_EMBED_HTML_PATTERN % data)

    def to_dict(self):
        return {
            'name': self.name,
            'video_url': self.get_absolute_url(),
            'embed_url': self.embed_url(),
            'user': unicode(self.user.userprofile.member.cast()),
            'views': self.views,
        }

    def video_age(self):
        """
        Returns a `timedelta` object representing the age of the video
        which is the difference between current time and the time when the
        video was submitted.
        """
        return timezone.now() - self.date_uploaded

    class Meta:
        permissions = (
            ('view_video', 'Can view videos'),
        )


class Comment(models.Model):
    """
    A model class for comments posted on videos.
    """
    video = models.ForeignKey(Video)
    user = models.ForeignKey(User)
    text = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s, %s' % (unicode(self.video), unicode(self.user))

    def __str__(self):
        return '%s, %s' % (str(self.video), str(self.user))

    def comment_age(self):
        """
        Returns a `timedelta` object representing the age of the Comment.
        (The difference between the current time and the time submitted.)
        """
        return timezone.now() - self.date_posted

    class Meta:
        permissions = (
            ('view_comment', 'Can view comments'),
        )


# Define a signal receiver for Video creation
@receiver(post_save, sender=Video)
def user_saved(sender, **kwargs):
    """
    A callback function for handling the post_save signal sent for Video
    objects.
    It sends a notification to the admins that a Video has been posted
    so that it can be approved.
    """
    created = kwargs.get('created')
    # Only send the notification if the object was created, not if it
    # is changed.
    if created:
        NAMED_URL_PATTERN = 'admin:distance_learning_video_change'
        video = kwargs.get('instance')
        send_admin_notification(message="A new video has been submitted.",
                                handle_url=urlresolvers.reverse(
                                    NAMED_URL_PATTERN,
                                    args=(video.id,)))
