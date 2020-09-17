from django import forms

from clubs.models import Club, ClubManagementPosition, Member
from fixtures.models import Umpire

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_select2.forms import HeavySelect2Widget, ModelSelect2Widget


class TransferRequestForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    transfer_from = forms.ModelChoiceField(queryset=Club.objects.all(), empty_label="Non-NEHL Club", required=False)
    evidence = forms.FileField(required=False)


class ClubManagementPositionWidget(forms.TextInput):
    def format_value(self, value):
        user = Member.objects.get(pk=value).user
        return user.first_name + ' ' + user.last_name


class EditClubManagementForm(forms.ModelForm):

    class Meta:
        model = ClubManagementPosition
        exclude = []
        widgets = {
            'holder': ClubManagementPositionWidget(),
            'type': forms.TextInput(),
            'club': forms.HiddenInput()
        }
        labels = {
            'type': 'Position'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['holder'].disabled = True
        else:
            self.fields['holder'].widget = HeavySelect2Widget(
                data_url='/clubs/api/17/members/'
            )


ClubManagementFormSet = forms.modelformset_factory(
    ClubManagementPosition,
    form=EditClubManagementForm,
    exclude=('club', ),
    can_delete=True
)


class ClubManagementFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ClubManagementFormSetHelper, self).__init__(*args, **kwargs)
        self.template = 'bootstrap/table_inline_formset.html'
        self.add_input(Submit('submit', 'Save Changes'))


UmpireFormSet = forms.modelformset_factory(
    Umpire,
    exclude=(),
)


class UmpireFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(UmpireFormSetHelper, self).__init__(*args, **kwargs)
        self.template = 'bootstrap/table_inline_formset.html'
        self.add_input(Submit('submit', 'Save Changes'))


class MemberRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class AdminMemberTransferForm(forms.Form):
    member = forms.ModelChoiceField(queryset=Member.objects.all(),
                                    widget=HeavySelect2Widget(data_url='/clubs/api/members/'))
    new_club = forms.ModelChoiceField(queryset=Club.objects.all())
