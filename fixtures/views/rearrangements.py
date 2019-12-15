from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.views.generic.edit import FormView
from django.template.loader import render_to_string

from fixtures.models import Fixture, RearrangementRequest, RearrangementResponse, FixtureRearrangement
from fixtures.forms import RearrangementRequestForm, RearrangementResponseForm, CreateRearrangement
from fixtures.utils.general import email_competition_admins, get_most_senior_parent_competition

from clubs.utils import email_main_club_contacts, email_notifications


from nehlwebsite.utils.auth_utils import can_manage_club, can_administrate_competition


@login_required
def index(request):
    rearrangement_requests = RearrangementRequest.objects.all().order_by('-date_time_created')
    user = request.user
    can_administrate = False

    if rearrangement_requests.count() > 0:
        if can_administrate_competition(user.id, rearrangement_requests.first().original_fixture.competition.id):
            can_administrate = True
    else:
        can_administrate = True

    if not can_administrate:
        return HttpResponseForbidden()

    paginator = Paginator(rearrangement_requests, 10)

    page = request.GET.get('page')
    rearrangement_requests = paginator.get_page(page)

    return render(request, 'rearrangements/index.html', {'rearrangements': rearrangement_requests})


@login_required
def detail(request, rearrangement_id):
    rearrangement_request = get_object_or_404(RearrangementRequest, pk=rearrangement_id)
    user = request.user
    can_administrate = False

    if can_administrate_competition(user.id, rearrangement_request.original_fixture.competition.id):
        can_administrate = True

    response = None

    if rearrangement_request.rearrangementresponse_set.count() > 0:
        response = rearrangement_request.rearrangementresponse_set.first()

    context = {'fixture': rearrangement_request.original_fixture,
               'response': response,
               'rearrangement': rearrangement_request,
               'can_administrate': can_administrate}

    return render(request, 'rearrangements/detail.html', context)


@login_required
def send_request(request, fixture_id):
    fixture = get_object_or_404(Fixture, pk=fixture_id)
    can_manage_fixture = False
    user = request.user

    if can_manage_club(user.id, fixture.team_a.club_id):
        can_manage_fixture = True
    if can_manage_club(user.id, fixture.team_b.club_id):
        can_manage_fixture = True

    if not can_manage_fixture:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = RearrangementRequestForm(request.POST)

        if form.is_valid():

            rearrangement_request = RearrangementRequest(
                original_fixture=fixture,
                reason=form.cleaned_data['reason'],
                new_date_time=form.cleaned_data['new_date_time'],
                status="requested",
                who_requested=user.member
            )
            rearrangement_request.save()

            email_context = {'request': rearrangement_request, 'fixture': fixture}

            msg_club_plain = render_to_string('email/club/fixture_rearrangement.txt', email_context)
            msg_club_html = render_to_string('email/club/fixture_rearrangement.html', email_context)
            msg_admin_plain = render_to_string('email/admin/fixture_rearrangement.txt', email_context)
            msg_admin_html = render_to_string('email/admin/fixture_rearrangement.html', email_context)
            msg_user_plain = render_to_string('email/user/fixture_rearrangement.txt', email_context)
            msg_user_html = render_to_string('email/user/fixture_rearrangement.html', email_context)
            subject = 'Rearrangement Request'

            email_main_club_contacts(fixture.team_a.club, subject, msg_club_plain, msg_club_html)
            email_main_club_contacts(fixture.team_b.club, subject, msg_club_plain, msg_club_html)
            parent_competition = get_most_senior_parent_competition(fixture.competition)
            email_competition_admins(parent_competition, subject, msg_admin_plain, msg_admin_html)
            email_notifications([user.email], subject, msg_user_plain, msg_user_html)

            return redirect('fixtures:detail', fixture_id=fixture_id)

    elif request.method == 'GET':

        form = RearrangementRequestForm()

    else:
        return HttpResponseBadRequest()

    context = {
        'fixture': fixture,
        'form': form,
    }

    return render(request, 'rearrangements/request.html', context)


@login_required
def respond(request, rearrangement_id):
    rearrangement_request = get_object_or_404(RearrangementRequest, pk=rearrangement_id)
    user = request.user
    can_administrate = False

    if can_administrate_competition(user.id, rearrangement_request.original_fixture.competition.id):
        can_administrate = True

    if not can_administrate:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = RearrangementResponseForm(request.POST)

        if form.is_valid():

            rearrangement_request.status = form.cleaned_data['answer']

            rearrangement_response = RearrangementResponse(
                answer=form.cleaned_data['answer'],
                reason=form.cleaned_data['reason'],
                request=rearrangement_request,
                responder=user
            )

            if form.cleaned_data['answer'] == 'Approved':

                old_fixture = rearrangement_request.original_fixture

                old_fixture.pk = None

                old_fixture.date = rearrangement_request.new_date_time.date()

                old_fixture.save()

                rearrangement = FixtureRearrangement(
                    creator=user,
                    from_fixture=rearrangement_request.original_fixture,
                    to_fixture=old_fixture,
                    reason=rearrangement_request.reason
                )

                rearrangement.save()
                rearrangement_request.save()

            fixture = rearrangement_request.original_fixture

            rearrangement_response.save()

            email_context = {'response': rearrangement_response, 'fixture': fixture}

            msg_plain = render_to_string('email/all/fixture_rearrangement_response.txt', email_context)
            msg_html = render_to_string('email/all/fixture_rearrangement_response.html', email_context)
            subject = 'Rearrangement Request'

            email_main_club_contacts(fixture.team_a.club, subject, msg_plain, msg_html)
            email_main_club_contacts(fixture.team_b.club, subject, msg_plain, msg_html)
            parent_competition = get_most_senior_parent_competition(fixture.competition)
            email_competition_admins(parent_competition, subject, msg_plain, msg_html)
            email_notifications([user.email], subject, msg_plain, msg_html)

            return redirect('rearrangements:detail', rearrangement_id=rearrangement_id)

    elif request.method == 'GET':

        form = RearrangementResponseForm()

    else:
        return HttpResponseBadRequest()

    return render(request, 'rearrangements/respond.html', {'form': form})


class RearrangementCreate(LoginRequiredMixin, FormView):
    form_class = CreateRearrangement
    template_name = 'rearrangements/create.html'
    success_url = '/clubs/'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):

        fixture_id = self.kwargs['fixture_id']

        fixture = get_object_or_404(Fixture, pk=fixture_id)

        if not can_administrate_competition(request.user.id, fixture.competition.id):
            raise Http404

        return super(RearrangementCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        fixture_id = self.kwargs['fixture_id']

        original_fixture = get_object_or_404(Fixture, pk=fixture_id)

        new_fixture = original_fixture

        new_fixture.pk = None

        new_fixture.date = form.cleaned_data['new_date_time'].date()

        new_fixture.save()

        original_fixture = get_object_or_404(Fixture, pk=fixture_id)

        rearrangement = FixtureRearrangement(
            creator=self.request.user,
            from_fixture=original_fixture,
            to_fixture=new_fixture,
            reason=form.cleaned_data['reason']
        )

        rearrangement.save()

        email_context = {'rearrangement': rearrangement, 'fixture': original_fixture}

        msg_plain = render_to_string('email/all/rearrangement_created.txt', email_context)
        msg_html = render_to_string('email/all/rearrangement_created.html', email_context)
        subject = 'Rearrangement Created'

        email_main_club_contacts(original_fixture.team_a.club, subject, msg_plain, msg_html)
        email_main_club_contacts(original_fixture.team_b.club, subject, msg_plain, msg_html)
        parent_competition = get_most_senior_parent_competition(original_fixture.competition)
        email_competition_admins(parent_competition, subject, msg_plain, msg_html)

        return super().form_valid(form)
