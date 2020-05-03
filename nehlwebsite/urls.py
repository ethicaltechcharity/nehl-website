"""nehlwebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from . import settings

from nehlwebsite import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('clubs/', include('clubs.urls')),
    path('fixtures/', include('fixtures.urls.fixtures')),
    path('fixtures/cancellations/', include('fixtures.urls.cancellations')),
    path('fixtures/rearrangements/', include('fixtures.urls.rearrangements')),
    path('fixtures/competitions/', include('fixtures.urls.competitions')),
    path('teams/', include('teams.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile', views.profile, name='profile')
]

# urlpatterns += path(settings.MEDIAFILES_LOCATION, 'https://nehl-web-files.s3.eu-west-2.amazonaws.com/')
