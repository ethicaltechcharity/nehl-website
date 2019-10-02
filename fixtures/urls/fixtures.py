from django.urls import path

from fixtures.views import fixtures

app_name = 'fixtures'
urlpatterns = [
    path('', fixtures.index, name='index'),
    path('<int:fixture_id>/cancel', fixtures.cancel, name='cancel'),
    path('original-card', fixtures.card_original),
    path('<int:fixture_id>', fixtures.detail, name='detail'),
    path('matchcardoriginals', fixtures.match_card_originals, name='matchcardoriginals')
]