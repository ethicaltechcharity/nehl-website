from django.urls import path

from fixtures.views import cancellations

app_name = 'cancellations'
urlpatterns = [
    path('', cancellations.index, name='index'),
    path('<cancellation_id>', cancellations.detail, name='detail'),
    path('respond/<cancellation_id>', cancellations.respond, name='respond'),
    path('delete/<int:pk>', cancellations.CancellationDelete.as_view(), name='delete')
]
