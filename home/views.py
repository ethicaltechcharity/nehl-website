from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.core.mail import send_mail

from fixtures.models import Competition
from home.forms import ContactForm


def index(request):
    return render(request, 'home/index.html')


def rules(request):
    nehl = get_object_or_404(Competition, pk=1)
    return render(request, 'home/rules.html', {"competition": nehl})


def help(request):
    return render(request, 'home/help.html')


def contact(request):

    if request.method == 'POST':

        form = ContactForm(request.POST)

        if form.is_valid():
            subject = "NEHL WEB CONTACT - " + form.cleaned_data['subject']
            sender = "notifications@northeasthockeyleague.org"
            message = "The following message was sent from the web contact form: \r\n\r\n" + \
                      form.cleaned_data['message'] + "\r\n\r\n" + \
                      "The message was sent by " + form.cleaned_data['sender']

            nehl = get_object_or_404(Competition, pk=1)

            recipients = []
            for official in nehl.officials.all():
                if official.type == 0:
                    try:
                        if official.user is not None:
                            recipients.append(official.user.email)
                    except:
                        pass

            send_mail(subject, message, sender, recipients)

            return HttpResponseRedirect('thanks')

    else:
        form = ContactForm()
    return render(request, 'home/contact.html',  {'form': form})


def thanks(request):
    return render(request, 'home/thanks.html')

