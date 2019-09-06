import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from fixtures.forms import FixtureCancellationForm
from fixtures.models import Fixture


def index(request):
    return HttpResponse('')


def cancel(request):

    if request.method == 'POST':

        form = FixtureCancellationForm(request.POST)

        if form.is_valid():

            return HttpResponseRedirect('home')

    elif request.method == 'GET':

        today = datetime.date.today()
        form = FixtureCancellationForm(initial={'fixture_date': today})

    else:
        return HttpResponseBadRequest()

    context = {
        'form': form,
    }

    return render(request, 'fixtures/cancel.html', context)


def card_original(request):
    return HttpResponse('')


def detail(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    return render(request, 'fixtures/detail.html', {'fixture': fixture})
