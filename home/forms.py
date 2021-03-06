from django import forms
from captcha.fields import ReCaptchaField


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField(label="Your Email")
    captcha = ReCaptchaField()

