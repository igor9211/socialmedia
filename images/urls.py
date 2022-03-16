from django.urls import path
from . import views

app_name = 'images'

urlpatterns = [
    path('create/', views.image_create, name='create'),
    path('detail/<int:id>/<slug:slug>/', views.image_detail, name='detail'),
    path('like/', views.image_like, name='like'),
    path('', views.image_list, name='list'),

    path('picture/', views.add_picture, name='picture'),
    path('list_picture/', views.list_picture, name='list_picture'),
    path('picture_detail/<int:id>/<slug:slug>/', views.picture_detail, name='picture_detail'),
    path('ranking/', views.image_ranking, name='create'),

]