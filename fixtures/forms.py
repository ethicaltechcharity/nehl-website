from django import forms
from fixtures.models import MatchCardImage, CancellationResponse, RearrangementRequest, RearrangementResponse, \
    Fixture


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
