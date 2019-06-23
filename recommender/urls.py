from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news/<str:category>/<int:newsId>/', views.content, name='contentPage'),	#categoryAndId = category/id
]
