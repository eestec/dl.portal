# Create your views here.
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from admin_notifications.models import AdminNotification

@staff_member_required
def show_all_notifications(request):
    """
    View which shows all admin notifications which have been registered.
    The number of notifications is limitted to 30 oldest notifications.
    """
    LIMIT_NOTIFICATION_NUMBER = 30
    notifications = AdminNotification.objects.all()[:30]
    return render_to_response(
                'admin/admin_notifications/show_all.html',
                {'notifications': notifications},
                context_instance=RequestContext(request))
@staff_member_required
def dismiss_notification(request, notification_id):
    """
    A view which dismisses the notification. It deletes the notification
    object from the database.
    """
    notification = get_object_or_404(AdminNotification, pk=notification_id)
    notification.delete()
    # TODO: Add a different response for AJAX requests
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

