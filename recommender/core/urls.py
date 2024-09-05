from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recommender/<str:user_id>/', views.job_recommendations, name='recommender')
]