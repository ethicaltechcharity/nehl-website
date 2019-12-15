from django import forms
from clubs.models import Club, ClubManagementPosition, Member
from crispy_forms.helper import FormHelper


class TransferRequestForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    transfer_from = forms.ModelChoiceField(queryset=Club.objects.all(), empty_label="Non-NEHL Club", required=False)
    evidence = forms.FileField(required=False)


class EditClubManagementForm(forms.ModelForm):

    class Meta:
        model = ClubManagementPosition
        exclude = ['club']
        widgets = {
            'type': forms.TextInput()
        }

    def __init__(self, club, *args, **kwargs):
        super(EditClubManagementForm, self).__init__(*args, **kwargs)
        self.fields['holder'].queryset = Member.objects.filter(club=club).all()


class BaseClubManagementFormSet(forms.BaseModelFormSet):

    class Meta:
        model = ClubManagementPosition

    def __init__(self, club, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = ClubManagementPosition.objects.filter(club=club).all()


ClubManagementFormSet = forms.modelformset_factory(
    ClubManagementPosition,
    exclude=('club', ),
    widgets={
        'holder': forms.TextInput(),
        'type': forms.TextInput()}
)


class ClubManagementFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ClubManagementFormSetHelper, self).__init__(*args, **kwargs)
        self.template = 'bootstrap/table_inline_formset.html'
