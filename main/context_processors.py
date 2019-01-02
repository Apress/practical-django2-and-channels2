import os
from django.conf import settings

def globals(request):
    data = {}
    data.update({
        'VERSION': os.environ.get("GIT_REV", ""),
        'GA_TRACKER_ID': settings.GA_TRACKER_ID,
    })
    return data
