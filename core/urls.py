from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('county/<str:code>/', views.CountyDetailView.as_view(), name='county_detail'),
    path('bill/<slug:slug>/', views.BillDetailView.as_view(), name='bill_detail'),
    path('bill/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/reply/', views.reply_to_comment, name='reply_to_comment'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('bill/create/', views.BillCreateView.as_view(), name='bill_create'),
    path('bill/<slug:slug>/edit/', views.BillUpdateView.as_view(), name='bill_edit'),
]
