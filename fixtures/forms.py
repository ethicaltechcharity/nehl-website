from django import forms
from django.forms import formset_factory, CheckboxInput
from django.shortcuts import get_object_or_404
from django_select2.forms import HeavySelect2Widget

from clubs.models import Member
from fixtures.models import MatchCardImage, CancellationResponse, RearrangementRequest, RearrangementResponse, \
    FixtureResult, Fixture

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div

from fixtures.utils.general import get_api_url

CANCELLATION_REASON_CHOICES = [
    ('PITCH_UNFIT', 'Pitch Unfit'),
    ('INSUFFICIENT_PLAYERS', 'Insufficient Players'),
    ('ADMINISTRATION_ERROR', 'Administration Error'),
    ('OTHER', 'Other')
]

CANCELLATION_RESPONSE_CHOICES = [
    ('Accepted', 'Accept'),
    ('Rejected', 'Reject')
]

CANCELLATION_TEAM_CHOICES = [
    ('Home Team', 'Home Team'),
    ('Away Team', 'Away Team')
]

REARRANGEMENT_RESPONSE_CHOICES = [
    ('Approved', 'Approve'),
    ('Rejected', 'Reject')
]


class ButtonCheckboxInput(CheckboxInput):
    template_name = 'django/forms/widgets/checkbox_option.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['wrap_label'] = True
        return context


class AppearanceForm(forms.Form):
    is_registered = forms.BooleanField(label='Registered',
        widget=ButtonCheckboxInput(attrs={'class': 'btn-group-toggle'})
        )
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    captain = forms.BooleanField()
    substitute = forms.BooleanField()

    def __init__(self, *args, team_id, fixture_id, **kwargs):
        super(AppearanceForm, self).__init__(*args, **kwargs)
        self.helper = AppearanceFormHelper()
        self.fields['member'] = forms.ModelChoiceField(
            queryset=Member.objects.none(),
            widget=HeavySelect2Widget(
                data_url=get_api_url(team_id)
            ))


class AppearanceFormHelper(FormHelper):
    form_class = 'form-inline form-horizontal'
    label_class = 'pr-2'
    field_class = 'px-2'
    layout = Layout(
        Div(
            'is_registered',
            'member',
            Div('first_name', 'last_name', style='display: none;'),
            'captain',
            'substitute',
            style='width: 100%;',
        )
    )
    # template = 'bootstrap/table_inline_formset.html'
    include_media = False


# class AppearancesFormset(forms.BaseModelFormSet):
#     pass

AppearancesFormset = formset_factory(
    AppearanceForm, min_num=7, extra=4, max_num=16, validate_max=True, validate_min=True)


class SubmitResultForm(forms.ModelForm):
    class Meta:
        model = FixtureResult
        fields = ('team_a_score', 'team_b_score')

    def __init__(self, fixture: Fixture, *args, **kwargs):
        super(SubmitResultForm, self).__init__(*args, **kwargs)
        self.fields['team_a_score'].label = fixture.team_a.__str__() + ' score:'
        self.fields['team_b_score'].label = fixture.team_b.__str__() + ' score:'
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Field('team_a_score', style='width:80px'),
            Field('team_b_score', style='width:80px')
        )


class FixtureCancellationForm(forms.Form):
    cancellation_reason = forms.ChoiceField(
        choices=CANCELLATION_REASON_CHOICES
    )
    who_cancelled = forms.ChoiceField(choices=CANCELLATION_TEAM_CHOICES)
    more_cancellation_info = forms.CharField(
        label="More Information",
        required=False,
        widget=forms.Textarea,
        max_length=150
    )


class CancellationResponseForm(forms.ModelForm):
    class Meta:
        model = CancellationResponse
        fields = ('response', 'additional_comments')
        widgets = {
            'response': forms.Select(choices=CANCELLATION_RESPONSE_CHOICES),
            'additional_comments': forms.Textarea()
        }


class RearrangementRequestForm(forms.ModelForm):
    class Meta:
        model = RearrangementRequest
        fields = ('new_date_time', 'reason')
        widgets = {
            'new_date_time': forms.DateInput(attrs={'id': 'datepicker'}),
            'reason': forms.Textarea()
        }
        labels = {
            'new_date_time': 'New Date'
        }


class RearrangementResponseForm(forms.ModelForm):
    class Meta:
        model = RearrangementResponse
        fields = ('answer', 'reason',)
        widgets = {
            'answer': forms.Select(choices=REARRANGEMENT_RESPONSE_CHOICES),
            'reason': forms.Textarea(),
        }
        labels = {
            'answer': 'Response'
        }


class CreateRearrangement(forms.Form):
    new_date_time = forms.DateTimeField(widget=forms.DateInput(attrs={'id': 'datepicker'}), label="New date")
    reason = forms.CharField(max_length=200, widget=forms.Textarea())


class MatchCardImageForm(forms.ModelForm):
    class Meta:
        model = MatchCardImage
        fields = ('image', 'name')
        labels = {
            'name': 'Fixture Name',
        }
        help_texts = {
            'name': 'eg. Carlisle 1s vs. Furness 3s',
        }
