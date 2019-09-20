from django import forms
from fixtures.models import MatchCardImage


CANCELLATION_REASON_CHOICES = [
    ('PITCH_UNFIT', 'Pitch Unfit'),
    ('INSUFFICIENT_PLAYERS', 'Insufficient Players'),
    ('ADMINISTRATION_ERROR', 'Administration Error'),
    ('OTHER', 'Other')
]


class FixtureCancellationForm(forms.Form):
    cancellation_reason = forms.ChoiceField(
        choices=CANCELLATION_REASON_CHOICES
    )
    more_cancellation_info = forms.CharField(
        label="More Information",
        required=False,
        widget=forms.Textarea,
        max_length=150
    )


class MatchCardImageForm(forms.ModelForm):
    class Meta:
        model = MatchCardImage
        fields = ('image', )
