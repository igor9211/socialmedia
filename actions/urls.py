from django.urls import path
from . import views

app_name = 'actions'

urlpatterns = [
    path('detail/', views.detail, name='detail'),

]