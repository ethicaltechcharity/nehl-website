from django import forms
from fixtures.models import MatchCardImage, CancellationResponse


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
