from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from clubs.models import Club, Member, TransferRequest, ClubManagementPosition
from clubs.forms import TransferRequestForm, ClubManagementFormSet, \
    ClubManagementFormSetHelper
from clubs.serializers import MemberSerializer

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
                ['danbaxter@live.co.uk', 'leighbrown@hotmail.co.uk'],
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
        formset = ClubManagementFormSet(queryset=ClubManagementPosition.objects.filter(club=club))
        for form in formset:
            form.fields['holder'].queryset = Member.objects.none()

    elif request.method == 'POST':
        formset = ClubManagementFormSet(request.POST, queryset=ClubManagementPosition.objects.filter(club=club))
        for form in formset:
            form.fields['holder'].queryset = Member.objects.filter(club=club)

        for form in formset.extra_forms:
            form.instance.club = club

        if formset.is_valid():
            formset.save()

        formset = ClubManagementFormSet(queryset=ClubManagementPosition.objects.filter(club=club))
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
                    search=SearchVector('user__first_name', 'user__last_name')
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


class MemberListAPI(ListModelMixin,
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
                    search=SearchVector('user__first_name', 'user__last_name')
                ).filter(
                    search__icontains=search_term
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


# class MemberRegister(LoginRequiredMixin, FormView):
#     template_name = 'contact.html'
#     form_class = ContactForm
#     success_url = '/thanks/'
