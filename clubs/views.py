from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from django.db.models import Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, FormView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from clubs.models import Club, Member, TransferRequest, ClubManagementPosition
from clubs.forms import TransferRequestForm, ClubManagementFormSet, \
    ClubManagementFormSetHelper, AdminMemberTransferForm, AdminMemberRegisterForm, AdminSetMainClubContactForm
from clubs.serializers import MemberSerializer, MemberPlusDOBSerializer
from clubs.utils import can_administrate_club

from nehlwebsite.utils.auth_utils import can_manage_club

import datetime


def index(request):
    clubs = Club.objects.order_by("name").all()
    return render(request, 'clubs/index.html', {'clubs': clubs})


def detail(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage = False
    user = request.user

    if user.is_authenticated:
        if can_manage_club(user.id, club_id):
            can_manage = True

    if club.secondary_colour == '#000000':
        light_or_dark = 'dark'
    else:
        light_or_dark = 'light'

    return render(request, 'clubs/detail.html',
                  {'club': club,
                   'can_manage': can_manage,
                   'light_or_dark': light_or_dark})


@login_required
def manage(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage = False
    user = request.user

    if can_manage_club(user.id, club_id):
        can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    context = {
        'club': club,
        'membership_size': club.members.count()
    }

    return render(request, 'clubs/manage.html', context)


@login_required
def request_transfer(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    can_manage = False
    user = request.user

    if can_manage_club(user.id, club_id):
        can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    if request.method == 'POST':

        form = TransferRequestForm(request.POST, request.FILES)

        if form.is_valid():

            if 'evidence' in form.files:
                evidence = form.files['evidence']
            else:
                evidence = None

            now = datetime.datetime.now()
            transfer_request = TransferRequest(
                datetime_submitted=now,
                submitter=user.member,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                date_of_birth=form.cleaned_data['date_of_birth'],
                transfer_from=form.cleaned_data['transfer_from'],
                transfer_to=club,
                evidence=evidence
            )
            transfer_request.save()

            msg_html = render_to_string('email/transfer-request-email.html',
                                        {'request': transfer_request})
            msg_plain = render_to_string('email/transfer-request-email.txt',
                                         {'request': transfer_request})

            send_mail(
                'Transfer Request',
                msg_plain,
                'notifications@northeasthockeyleague.org',
                ['danbaxter@live.co.uk', 'nehlsecretary@gmail.com', 'nehlc@live.co.uk'],
                html_message=msg_html,
            )

            return render(request, 'clubs/members/transfer-request-sent.html')

    elif request.method == 'GET':

        form = TransferRequestForm()

    else:
        return HttpResponseBadRequest()

    return render(request, 'clubs/members/transfer-request.html', {'form': form})


@login_required
def edit_club_contacts(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    user = request.user
    can_manage = False

    if can_manage_club(user.id, club_id):
        can_manage = True

    if not can_manage:
        return HttpResponseForbidden()

    if request.method == 'GET':
        formset = ClubManagementFormSet(queryset=ClubManagementPosition.objects.filter(club=club),
                                        form_kwargs={'club': club})
        for form in formset:
            form.fields['holder'].queryset = Member.objects.none()

    elif request.method == 'POST':
        formset = ClubManagementFormSet(request.POST,
                                        queryset=ClubManagementPosition.objects.filter(club=club),
                                        form_kwargs={'club': club})
        for form in formset:
            form.fields['holder'].queryset = Member.objects.filter(club=club)

        for form in formset.extra_forms:
            form.instance.club = club

        if formset.is_valid():
            formset.save()

        formset = ClubManagementFormSet(queryset=ClubManagementPosition.objects.filter(club=club),
                                        form_kwargs={'club': club})
        for form in formset:
            form.fields['holder'].queryset = Member.objects.filter(club=club)

    else:
        return HttpResponseBadRequest()

    return render(request, 'clubs/contacts/edit.html', {'formset': formset, 'helper': ClubManagementFormSetHelper()})


# @login_required
# def edit_club_umpires(request, club_id):
#     club = get_object_or_404(Club, pk=club_id)
#     user = request.user
#     can_manage = False
#
#     if can_manage_club(user.id, club_id):
#         can_manage = True
#
#     if not can_manage:
#         return HttpResponseForbidden()
#
#     # if request.method == 'GET':
#     formset = UmpireFormSet()
#
#     return render(request, 'clubs/umpires/edit.html', {'formset': formset, 'helper': UmpireFormSetHelper()})


class MemberList(LoginRequiredMixin, ListView):
    model = Member
    context_object_name = 'members'
    template_name = 'clubs/members/list.html'
    paginate_by = 10
    login_url = '/accounts/login/'

    def get_queryset(self):
        queryset = Member.objects.filter(
            club=get_object_or_404(Club, pk=self.kwargs['club_id'])
        )
        if 'search' in self.request.GET:
            if self.request.GET['search'] != '':
                search_term = self.request.GET.get('search', '')
                queryset = queryset.annotate(
                    search=Concat('user__first_name', Value(' '), 'user__last_name')
                ).filter(
                    search__icontains=search_term
                )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MemberList, self).get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['club_id'] = self.kwargs['club_id']
        return context

    def dispatch(self, request, *args, **kwargs):

        if not can_manage_club(request.user.id, self.kwargs['club_id']):
            return HttpResponseForbidden()

        return super(MemberList, self).dispatch(request, *args, **kwargs)


class ClubMemberListAPI(ListModelMixin,
                        GenericAPIView):
    model = Member
    serializer_class = MemberSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Member.objects.filter(
            club=get_object_or_404(Club, pk=self.kwargs['club_id'])
        )
        if 'search' in self.request.GET:
            if self.request.GET['search'] != '':
                search_term = self.request.GET.get('search', '')
                queryset = queryset.annotate(
                    search=Concat('user__first_name', Value(' '), 'user__last_name')
                ).filter(
                    search__icontains=search_term
                )
        return queryset


class MemberListAPI(ListModelMixin, GenericAPIView):
    model = Member
    serializer_class = MemberPlusDOBSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Member.objects.all()
        if 'search' in self.request.GET:
            if self.request.GET['search'] != '':
                search_term = self.request.GET.get('search', '')
                queryset = queryset.annotate(
                    # search=SearchVector('user__first_name', 'user__last_name'),
                    full_name=Concat('user__first_name', Value(' '), 'user__last_name'),
                ).filter(
                    full_name__icontains=search_term
                )
        return queryset


class MemberDetail(LoginRequiredMixin, DetailView):
    model = Member
    context_object_name = 'member'
    template_name = 'clubs/members/detail.html'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):

        if not can_manage_club(request.user.id, self.kwargs['club_id']):
            return HttpResponseForbidden()

        return super(MemberDetail, self).dispatch(request, *args, **kwargs)


class AdminMemberTransfer(LoginRequiredMixin, FormView):
    form_class = AdminMemberTransferForm
    template_name = 'clubs/members/admin-transfer.html'
    success_url = '/accounts/profile'

    def form_valid(self, form):
        member = form.cleaned_data['member']
        new_club = form.cleaned_data['new_club']
        member.club = new_club
        member.save()
        return super().form_valid(form)


class AdminMemberRegister(LoginRequiredMixin, FormView):
    template_name = 'clubs/members/admin-register.html'
    form_class = AdminMemberRegisterForm
    success_url = '/accounts/profile'

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        user = User.objects.create_user(self.build_username(first_name, last_name))
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        member = Member()
        member.user = user
        member.date_of_birth = form.cleaned_data['date_of_birth']
        member.club = form.cleaned_data['club']
        member.registration_date = datetime.datetime.now().date()
        member.save()

        return super().form_valid(form)

    def build_username(self, first_name, last_name):
        attempt = 0

        while True:
            username = first_name[0] + "." + last_name
            username = username.lower()

            if attempt > 0:
                username += "." + str(attempt)

            if User.objects.filter(username=username).count() == 0:
                return username

            attempt += 1


class AdminSetMainClubContact(LoginRequiredMixin, FormView):
    form_class = AdminSetMainClubContactForm
    success_url = ''
    template_name = 'clubs/admin/set-main-club-contact.html'

    def get(self, request, *args, **kwargs):
        club = get_object_or_404(Club, pk=self.kwargs['club_id'])
        if not can_administrate_club(request.user.id, club):
            return HttpResponseForbidden()

    def get_success_url(self):
        return '/clubs/' + str(self.kwargs['club_id']) + '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'club_id': self.kwargs['club_id']})
        return kwargs

    def get_context_data(self, **kwargs):
        club = get_object_or_404(Club, pk=self.kwargs['club_id'])
        context = super(AdminSetMainClubContact, self).get_context_data()
        context.update({'club': club})
        return context

    def form_valid(self, form):
        club = get_object_or_404(Club, pk=self.kwargs['club_id'])
        club.main_contact = form.cleaned_data['new_contact']
        club.save()
        return super().form_valid(form)
