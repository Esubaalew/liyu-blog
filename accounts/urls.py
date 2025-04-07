from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.public_profile_view, name='public_profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
