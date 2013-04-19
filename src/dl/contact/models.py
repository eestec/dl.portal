from django.db import models
from django.core import urlresolvers
from django.dispatch import receiver
from django.db.models.signals import post_save

from admin_notifications.models import AdminNotification

# Create your models here.

class BugReport(models.Model):
    email_address = models.EmailField(
        help_text=u'An email address where we can contact you')
    error_summary = models.CharField(max_length=150)
    description = models.TextField(
        help_text=u'Give as many details as possible about the error')
    screenshot = models.ImageField(
            upload_to=lambda instance, filename: '/'.join(('bugs',
                                                           'screenshots',
                                                           filename)),
            blank=True)

    def __unicode__(self):
        return self.error_summary


@receiver(post_save, sender=BugReport)
def bug_report_saved(sender, **kwargs):
    """
    A signal receiver which fires after a BugReport is saved.
    It is used to add an admin notification that there has been a new
    bug report.
    """
    created = kwargs.get('created')
    if created:
        bug_report = kwargs.get('instance')
        notification = AdminNotification(
            message=u'A new bug report has been filed.',
            handle_url=urlresolvers.reverse('admin:contact_bugreport_change',
                                            args=(bug_report.id,)),
            app_name='contact')
        notification.save()
