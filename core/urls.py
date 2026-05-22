from django.urls import path
from . import views

urlpatterns = [
    # General Routing
    path('', views.home, name='home'),
    path('home-original/', views.home_original, name='home_original'),
    path('home-option-a/', views.home_option_a, name='home_option_a'),
    path('home-option-b/', views.home_option_b, name='home_option_b'),
    path('home-option-c/', views.home_option_c, name='home_option_c'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # Kitchen Operations
    path('kitchen/dashboard/', views.kitchen_dashboard, name='kitchen_dashboard'),
    path('kitchen/safety-log/', views.safety_log_post, name='safety_log_post'),

    # GIS Dispatch Routing
    path('dispatch/queue/', views.dispatch_queue, name='dispatch_queue'),
    path('dispatch/allocate/', views.allocate_route, name='allocate_route'),

    # Donor & Fundraising
    path('donor/portal/', views.donor_portal, name='donor_portal'),

    # MIS Dashboard
    path('admin/mis/dashboard/', views.mis_dashboard, name='mis_dashboard'),
]
