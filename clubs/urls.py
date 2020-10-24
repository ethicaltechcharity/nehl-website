from django.contrib.auth.decorators import login_required
from django.urls import path


from . import views

app_name = 'clubs'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:club_id>/', views.detail, name='detail'),
    path('<int:club_id>/manage/', views.manage, name='manage'),
    path('<int:club_id>/manage/contacts/', views.edit_club_contacts, name='edit-contacts'),
    # path('manage/<int:club_id>/umpires/', views.edit_club_umpires, name='edit-umpires'),
    path('<int:club_id>/members/', views.MemberList.as_view(), name='members-list'),
    path('api/<int:club_id>/members/', views.ClubMemberListAPI.as_view(), name='api-members-list'),
    path('api/members/', views.MemberListAPI.as_view(), name='api-all-members-list'),
    path('<int:club_id>/members/<int:pk>/', views.MemberDetail.as_view(), name='members-detail'),
    path('<int:club_id>/members/request-transfer/', views.request_transfer, name='request-transfer'),
    path('transfer/', views.AdminMemberTransfer.as_view(), name='admin-member-transfer'),
    path('members/register/', views.AdminMemberRegister.as_view(), name='admin-member-register'),
    path('<int:club_id>/admin/set-main-contact/', views.AdminSetMainClubContact.as_view(), name='admin-set-main-contact')
]
