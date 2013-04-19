from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy
from contact.models import BugReport


class BugReportCreate(CreateView):
    model = BugReport
    success_url = reverse_lazy('dl-report-success')
    template_name = 'distance_learning/report-about.html'
