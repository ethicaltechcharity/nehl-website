from django.urls import path

from fixtures.views import rearrangements

app_name = 'rearrangements'
urlpatterns = [
    path('', rearrangements.index, name='index'),
    path('<fixture_id>/create', rearrangements.RearrangementCreate.as_view(), name='create'),
    path('<rearrangement_id>', rearrangements.detail, name='detail'),
    path('<fixture_id>/rearrange', rearrangements.send_request, name='request'),
    path('<rearrangement_id>/respond', rearrangements.respond, name='respond'),
]
