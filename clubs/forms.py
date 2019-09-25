from django import forms
from clubs.models import Club


class TransferRequestForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    transfer_from = forms.ModelChoiceField(queryset=Club.objects.all(), empty_label="Non-NEHL Club", required=False)
    evidence = forms.FileField(required=False)
