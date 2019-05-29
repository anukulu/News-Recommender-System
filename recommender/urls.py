from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news/<int:newsId>/', views.content, name='contentPage'),
]
