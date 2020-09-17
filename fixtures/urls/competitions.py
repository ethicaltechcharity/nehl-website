from django.urls import path

from fixtures.views import competitions

app_name = 'competitions'
urlpatterns = [
    path('', competitions.CompetitionListView.as_view(), name='index'),
    path('<int:pk>', competitions.CompetitionDetailView.as_view(), name='detail'),
    path('<int:competition>/admin', competitions.CompetitionAdminView.as_view(), name='admin'),
    path('<int:competition>/seasons/<int:season>/standings',
         competitions.CompetitionStandingsView.as_view(), name='standings'),
    path('<int:competition>/seasons/<int:season>/admin',
         competitions.SeasonAdminView.as_view(), name='season-admin'),
    path('<int:competition>/seasons/<int:season>/issues',
         competitions.SeasonIssuesView.as_view(), name='season-issues'),
    path('<int:competition>/seasons/create',
         competitions.SeasonCreateView.as_view(), name='season-create'),
]
