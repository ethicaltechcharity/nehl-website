from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rules', views.rules, name='rules'),
    path('accounts/', include(('django.contrib.auth.urls', 'django.contrib.auth'), namespace='accounts')),
    path('accounts/profile', views.profile)
]
