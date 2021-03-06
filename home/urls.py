from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rules', views.rules, name='rules'),
    path('contact', views.contact, name='contact'),
    path('thanks', views.thanks, name='thanks'),
    path('help', views.help, name='help')
]

