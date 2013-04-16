from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse
from contact.models import BugReport


class BugReportCreate(CreateView):
    model = BugReport
    template_name = 'distance_learning/report-about.html'
