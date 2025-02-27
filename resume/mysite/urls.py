from django.urls import path
from . import views
from .views import send_message

urlpatterns = [
    path('', views.index, name='index'),
    path("send-message/", send_message, name="send_message"),
]