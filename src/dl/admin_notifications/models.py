from django.db import models

# Create your models here.
class AdminNotification(models.Model):
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    # The URL to follow to handle/get extra info about the notification
    handle_url = models.URLField(blank=True)
    # Which app pushed the notification
    app_name = models.CharField(max_length=20)
