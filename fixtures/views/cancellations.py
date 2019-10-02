from django.shortcuts import render, get_object_or_404

from fixtures.models import FixtureCancellation
from fixtures.forms import CancellationResponseForm
from fixtures.utils.cancellations import can_manage_cancellation

from django.http import HttpResponseRedirect, HttpResponseForbidden


def index(request):
    cancellations = FixtureCancellation.objects.all().order_by('-datetime_cancelled')
    user = request.user
    can_manage = False

    if user.is_authenticated:
        if can_manage_cancellation(cancellations.first(), user.id):
            can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    return render(request, 'cancellations/index.html', {'cancellations': cancellations})


def detail(request, cancellation_id):
    cancellation = get_object_or_404(FixtureCancellation, pk=cancellation_id)
    user = request.user
    can_manage = False

    if user.is_authenticated:
        if can_manage_cancellation(cancellation, user.id):
            can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    return render(request, 'cancellations/detail.html', {'fixture': cancellation.fixture, 'cancellation': cancellation})


def respond(request, cancellation_id):
    cancellation = get_object_or_404(FixtureCancellation, pk=cancellation_id)
    user = request.user
    can_manage = False

    if user.is_authenticated:
        if can_manage_cancellation(cancellation, user.id):
            can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = CancellationResponseForm(request.POST)

        if form.is_valid():

            return HttpResponseRedirect('index')

    else:
        form = CancellationResponseForm()

    return render(request, 'cancellations/respond.html', {'cancellation': cancellation, 'form': form})
