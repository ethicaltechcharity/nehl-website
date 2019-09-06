from django.urls import path

from . import views

app_name = 'fixtures'
urlpatterns = [
    path('', views.index, name='index'),
    path('cancel', views.cancel),
    path('original-card', views.card_original),
    path('<int:fixture_id>', views.detail, name='detail')
]
