from django.shortcuts import render

from fixtures.models import FixtureCancellation


def index(request):
    cancellations = FixtureCancellation.objects.all().order_by('-datetime_cancelled')
    return render(request, 'cancellations/index.html', {'cancellations': cancellations})
