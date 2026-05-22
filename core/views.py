from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# 1. Public Homepage View Variants
def home(request):
    return render(request, 'home_option_a.html') # Active default Option A

def home_original(request):
    return render(request, 'home_original.html')

def home_option_a(request):
    return render(request, 'home_option_a.html')

def home_option_b(request):
    return render(request, 'home_option_b.html')

def home_option_c(request):
    return render(request, 'home_option_c.html')

# 2. Onboarding & Authentication Placeholders (Sprint 1+)
def register(request):
    # Query parameters can determine the active role tab on render (e.g. ?role=member)
    role = request.GET.get('role', 'member')
    tab = request.GET.get('tab', 'register')
    context = {'active_role': role, 'active_tab': tab}
    return render(request, 'register.html', context)

def user_login(request):
    return redirect('home')

def user_logout(request):
    logout(request)
    return redirect('home')

# 3. Kitchen Dashboard Placeholders (Sprint 2)
def kitchen_dashboard(request):
    return render(request, 'kitchen.html')

def safety_log_post(request):
    return JsonResponse({'status': 'pending'})

# 4. Dispatch & Logistics Placeholders (Sprint 3)
def dispatch_queue(request):
    return render(request, 'dispatch.html')

def allocate_route(request):
    return JsonResponse({'status': 'pending'})

# 5. Donor Portal Placeholders (Sprint 4)
def donor_portal(request):
    return render(request, 'donor.html')

# 6. MIS Executive Dashboard (Sprint 5)
def mis_dashboard(request):
    return render(request, 'dashboard.html')
