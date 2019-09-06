from django.urls import path

from . import views

app_name = 'clubs'
urlpatterns = [
    path('', views.index, name='index'),
    path('view', views.view),
    path('<int:club_id>/', views.detail, name='detail')
]
