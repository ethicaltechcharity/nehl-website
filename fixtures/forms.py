from datetime import datetime

from django import forms
from django.forms import formset_factory, CheckboxInput
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.core.exceptions import ValidationError

from clubs.models import Member, Club
from fixtures.models import MatchCardImage, CancellationResponse, RearrangementRequest, RearrangementResponse, \
    FixtureResult, Fixture, Competition, Appearance, PersonalPenaltyType
from fixtures.utils.general import get_api_url
from teams.models import Team

from django_select2.forms import HeavySelect2Widget, ModelSelect2MultipleWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, Fieldset

import pandas

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


class MemberChoiceField(forms.ModelChoiceField):
    validators = [validators.integer_validator]

    default_error_messages = {
        'required': _('You must select a player.'),
    }

    def __init__(self, team_id, initial=None):
        self.team_id = team_id
        self.club = Team.objects.get(pk=team_id).club
        super(MemberChoiceField, self).__init__(
            label='Registered Player',
            initial=initial,
            required=False,
            queryset=Member.objects.none(),
            widget=HeavySelect2Widget(
                data_url=get_api_url(team_id)
            ))

    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            if isinstance(value, self.queryset.model):
                value = getattr(value, key)
            value = self.club.members.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value


class AppearanceForm(forms.Form):
    is_registered = forms.BooleanField(label='Registered', required=False, initial=True,
                                       widget=ButtonCheckboxInput(
                                           attrs={'class': 'btn-group-toggle'})
                                       )
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, team_id, fixture_id, **kwargs):
        super(AppearanceForm, self).__init__(*args, **kwargs)
        self.helper = AppearanceFormHelper()
        self.fields['member'] = MemberChoiceField(team_id)

    def clean(self):
        if self.cleaned_data['is_registered']:
            self.fields['member'].required = True
            self.fields['member'].validate(self.data[self.prefix + '-member'])
        else:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True
            self.fields['first_name'].validate(self.cleaned_data['first_name'])
            self.fields['last_name'].validate(self.cleaned_data['last_name'])


class AppearanceFormHelper(FormHelper):
    form_class = 'form-inline form-horizontal'
    label_class = 'pr-2'
    field_class = 'px-2'
    include_media = False


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


class ScorerForm(forms.Form):

    def __init__(self, fixture: Fixture, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scorer'] = forms.ModelChoiceField(queryset=fixture.appearance_set.all())
        self.fields['number'] = forms.IntegerField(min_value=1, label='Number scored')


class ScorerFormsetHelper(FormHelper):
    form_class = 'card card-body form-horizontal form-inline'
    label_class = 'pr-2'
    field_class = 'px-2'
    include_media = False
    form_tag = False
    layout = Layout(
        Div(
            Div('scorer', css_class='col-12 col-sm-4'),
            Div('number', css_class='col-12 col-sm-4'),
            css_class='row scorer-row my-2'
        )
    )


ScorerFormset = formset_factory(ScorerForm, max_num=32, min_num=0, validate_max=True)


class PenaltyForm(forms.Form):
    def __init__(self, fixture: Fixture, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'] = forms.ModelChoiceField(queryset=fixture.appearance_set.all())
        self.fields['type'] = forms.ModelChoiceField(queryset=PersonalPenaltyType.objects.all())


class PenaltyFormsetHelper(FormHelper):
    form_class = 'card card-body form-horizontal form-inline'
    label_class = 'pr-2'
    field_class = 'px-2'
    include_media = False
    form_tag = False
    layout = Layout(
        Div(
            Div('recipient', css_class='col-12 col-sm-4'),
            Div('type', css_class='col-12 col-sm-4'),
            css_class='row penalty-row my-2'
        )
    )


PenaltyFormset = formset_factory(PenaltyForm, max_num=32, min_num=0, validate_max=True)


class MatchCardForm(forms.Form):
    image = forms.ImageField()


class CSVFileField(forms.FileField):

    def validate(self, value):
        try:
            data = pandas.read_csv(value)
        except:
            raise ValidationError('Error decoding file.')

        for n, row in data.iterrows():
            try:
                date_str = row['date']
                club_a_str = row['club_a']
                team_a_str = row['team_a']
                club_b_str = row['club_b']
                team_b_str = row['team_b']
            except KeyError:
                raise ValidationError('File does not correspond to required structure.')

            try:
                club_a = Club.objects.get(short_name__iexact=club_a_str)
                club_b = Club.objects.get(short_name__iexact=club_b_str)
                Team.objects.get(club=club_a, short_name__iexact=team_a_str)
                Team.objects.get(club=club_b, short_name__iexact=team_b_str)
            except:
                raise ValidationError('Clubs or teams not recognised.')

            try:
                datetime.strptime(date_str, '%d/%m/%Y')
            except ValueError:
                raise ValidationError('Unable to parse date, is it in the correct format (dd/mm/yy)?')

        super().validate(value)


class SeasonCreateForm(forms.Form):
    display_name = forms.CharField(max_length=5, help_text='e.g. 20/21')
    years = forms.CharField(max_length=6, help_text='e.g. 202021')
    fixtures_file = CSVFileField()

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
