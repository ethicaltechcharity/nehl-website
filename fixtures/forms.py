from django import forms


class FixtureCancellationForm(forms.Form):
    team_one = forms.ChoiceField(label="Home Team")
    team_two = forms.ChoiceField(label="Away Team")
    division = forms.ChoiceField()
    fixture_date = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={
            'class': 'datepicker'
        }))
    team_that_cancelled = forms.ChoiceField()
    cancellation_reason = forms.ChoiceField()
    more_cancellation_info = forms.Textarea()

