from . import views
from django.urls import path

app_name='circle'
urlpatterns=[
    path('', views.home, name='home')
]