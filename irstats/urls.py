from django.urls import path

from . import views

app_name = 'irstats'
urlpatterns = [
    path('', views.index, name='index'),
]