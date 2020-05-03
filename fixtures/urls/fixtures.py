from django.urls import path

from fixtures.views import fixtures
from fixtures.views.fixtures import SelectSquadView

app_name = 'fixtures'
urlpatterns = [
    path('', fixtures.index, name='index'),
    path('<int:fixture_id>/cancel', fixtures.cancel, name='cancel'),
    path('<int:fixture_id>/submit-result', fixtures.submit_result, name='submit-result'),
    path('<int:fixture_id>/select-squad/<int:team_id>/', SelectSquadView.as_view(), name='submit-result'),
    path('original-card', fixtures.card_original),
    path('<int:fixture_id>', fixtures.detail, name='detail'),
    path('matchcardoriginals', fixtures.match_card_originals, name='matchcardoriginals')
]