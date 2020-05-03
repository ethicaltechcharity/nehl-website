from django.urls import path

from fixtures.views import competitions

app_name = 'competitions'
urlpatterns = [
    path('', competitions.index, name='index'),
    path('<int:pk>', competitions.CompetitionDetailView.as_view(), name='detail')
]