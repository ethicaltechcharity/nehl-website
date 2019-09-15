from django.urls import path

from . import views

app_name = 'clubs'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:club_id>/', views.detail, name='detail'),
    path('manage/<int:club_id>', views.manage, name='manage'),
    path('<int:club_id>/members/request-transfer', views.request_transfer, name='request-transfer')
]
