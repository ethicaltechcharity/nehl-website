from django.contrib.auth.forms import PasswordResetForm

from django.contrib.auth.models import User

for user in User.objects.all():
    reset_form = PasswordResetForm()
    reset_form.cleaned_data = {}
    reset_form.cleaned_data["email"] = user.username
    reset_form.save(domain_override="northeasthockeyleague.org")
