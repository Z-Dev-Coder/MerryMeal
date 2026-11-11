from django.urls import path
from . import views

urlpatterns = [
    # General Routing
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('register/approve-simulated/', views.approve_simulated_email, name='approve_simulated_email'),
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

    # Active Kitchens API for Geofencing map coordinates
    path('api/active-kitchens/', views.active_kitchens, name='active_kitchens'),
]
