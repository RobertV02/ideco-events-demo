from django.urls import path
from .views import event_list, event_detail

urlpatterns = [
    path('', event_list, name='events'),
    path('event/<int:pk>/', event_detail, name='event_detail'),
]