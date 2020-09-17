from django.urls import path

from fixtures.views import fixtures
from fixtures.views.fixtures import SelectSquadView, SubmitScorersView, SubmitPenaltiesView, SubmitMatchCardView

app_name = 'fixtures'
urlpatterns = [
    path('', fixtures.index, name='index'),
    path('<int:fixture_id>', fixtures.detail, name='detail'),
    path('<int:fixture_id>/cancel', fixtures.cancel, name='cancel'),
    path('<int:fixture_id>/submit-result', fixtures.submit_result, name='submit-result'),
    path('<int:fixture_id>/submit-scorers', SubmitScorersView.as_view(), name='submit-scorers'),
    path('<int:fixture_id>/submit-penalties', SubmitPenaltiesView.as_view(), name='submit-penalties'),
    path('<int:fixture_id>/submit-match-card', SubmitMatchCardView.as_view(), name='submit-match-card'),
    path('<int:fixture_id>/select-squad/<int:team_id>/', SelectSquadView.as_view(), name='select-squad'),
    path('original-card', fixtures.card_original),
    path('matchcardoriginals', fixtures.match_card_originals, name='matchcardoriginals')
]
