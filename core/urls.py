from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('county/<int:county_id>/', views.county_detail, name='county_detail'),
    path('county/<int:county_id>/bill/<slug:bill_slug>/', views.bill_detail, name='bill_detail'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]
