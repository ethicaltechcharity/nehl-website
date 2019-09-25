from django.urls import path

from fixtures.views import cancellations

app_name = 'fixtures'
urlpatterns = [
    path('', cancellations.index, name='cancellations.index')
]
