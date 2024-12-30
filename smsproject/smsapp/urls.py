from django.urls import path
from .views import SendSMSAPIView

urlpatterns = [
    path('send-sms/', SendSMSAPIView.as_view(), name='send_sms'),
]