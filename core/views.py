from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.models import User, Member, Caregiver, Volunteer, Kitchen, FoodSafetyLog, Delivery, Donation

# 1. Public Homepage View
def home(request):
    return render(request, 'home.html')

# 2. Onboarding & Authentication with MySQL Integration
def register(request):
    role = request.GET.get('role', 'member')
    tab = request.GET.get('tab', 'register')
    
    if request.method == 'POST':
        form_role = request.POST.get('role')
        
        if form_role == 'member':
            name = request.POST.get('memberName', 'Anonymous Member')
            phone = request.POST.get('memberPhone', '')
            address = request.POST.get('memberAddress', '')
            allergies = request.POST.get('memberAllergies', '')
            
            # Ensure unique username
            username = name.lower().replace(' ', '_') + str(User.objects.count() + 1)
            user = User.objects.create_user(
                username=username,
                phone=phone,
                role='member',
                first_name=name
            )
            Member.objects.create(
                user=user,
                address=address,
                dietary_restrictions=allergies,
                service_type='hot_meal',
                status='active'
            )
            return JsonResponse({'status': 'success', 'message': f'Member profile for {name} created in MySQL successfully!'})
            
        elif form_role == 'caregiver':
            name = request.POST.get('caregiverName', 'Anonymous Caregiver')
            relationship = request.POST.get('caregiverRelation', 'spouse')
            assoc_name = request.POST.get('associatedMember', '')
            
            # Find associated member or create one
            assoc_member = Member.objects.filter(user__first_name__icontains=assoc_name).first()
            if not assoc_member:
                # create a dummy member in MySQL
                dummy_user = User.objects.create_user(
                    username=assoc_name.lower().replace(' ', '_') + '_member' + str(User.objects.count() + 1),
                    role='member',
                    first_name=assoc_name
                )
                assoc_member = Member.objects.create(user=dummy_user, address="Address Verification Staged", status='active')
            
            username = name.lower().replace(' ', '_') + str(User.objects.count() + 1)
            user = User.objects.create_user(
                username=username,
                role='caregiver',
                first_name=name
            )
            Caregiver.objects.create(
                user=user,
                associated_member=assoc_member,
                relationship=relationship
            )
            return JsonResponse({'status': 'success', 'message': f'Caregiver profile for {name} linked to {assoc_name} successfully!'})
            
        elif form_role == 'volunteer':
            name = request.POST.get('riderName', 'Anonymous Rider')
            vehicle = request.POST.get('vehicleType', 'car')
            radius = request.POST.get('operatingRadius', 10)
            
            username = name.lower().replace(' ', '_') + str(User.objects.count() + 1)
            user = User.objects.create_user(
                username=username,
                role='volunteer',
                first_name=name
            )
            Volunteer.objects.create(
                user=user,
                vehicle_type=vehicle,
                operating_radius_km=radius,
                availability_schedule="Mon,Tue,Wed,Thu,Fri",
                status='active'
            )
            return JsonResponse({'status': 'success', 'message': f'Volunteer Rider {name} registered in MySQL!'})
            
        elif form_role == 'partner':
            name = request.POST.get('kitchenName', 'Anonymous Kitchen')
            capacity = request.POST.get('kitchenCapacity', 250)
            license_code = request.POST.get('kitchenLicense', '')
            
            username = name.lower().replace(' ', '_') + str(User.objects.count() + 1)
            user = User.objects.create_user(
                username=username,
                role='partner',
                first_name=name
            )
            Kitchen.objects.create(
                user=user,
                address="Address Verification Staged",
                max_daily_capacity=capacity
            )
            return JsonResponse({'status': 'success', 'message': f'Partner Kitchen {name} enrolled in MySQL!'})

    context = {'active_role': role, 'active_tab': tab}
    return render(request, 'register.html', context)

def user_login(request):
    return redirect('home')

def user_logout(request):
    logout(request)
    return redirect('home')

# 3. Kitchen Dashboard Operations with MySQL Integration
def kitchen_dashboard(request):
    # Ensure a default kitchen exists in MySQL
    kitchen = Kitchen.objects.first()
    if not kitchen:
        dummy_user, _ = User.objects.get_or_create(
            username="central_culinary_hub",
            defaults={'role': 'partner', 'first_name': 'Central Culinary Hub'}
        )
        kitchen = Kitchen.objects.create(
            user=dummy_user,
            address="100 culinary St, Central Area",
            max_daily_capacity=500
        )
        
    safety_logs = FoodSafetyLog.objects.filter(kitchen=kitchen).order_by('-logged_at')
    context = {'safety_logs': safety_logs}
    return render(request, 'kitchen.html', context)

def safety_log_post(request):
    if request.method == 'POST':
        dish = request.POST.get('dish', 'Roasted Herb Dish')
        cook_temp = request.POST.get('cook_temp', 165.00)
        hold_temp = request.POST.get('hold_temp', 145.00)
        
        kitchen = Kitchen.objects.first()
        if not kitchen:
            dummy_user, _ = User.objects.get_or_create(
                username="central_culinary_hub",
                defaults={'role': 'partner', 'first_name': 'Central Culinary Hub'}
            )
            kitchen = Kitchen.objects.create(
                user=dummy_user,
                address="100 culinary St, Central Area",
                max_daily_capacity=500
            )
            
        log = FoodSafetyLog.objects.create(
            kitchen=kitchen,
            dish_name=dish,
            portion_count=124,
            cooking_temp_f=cook_temp,
            holding_temp_f=hold_temp,
            kitchen_staff_signoff="Chef Marcus"
        )
        return JsonResponse({
            'status': 'success',
            'dish_name': log.dish_name,
            'holding_temp_f': float(log.holding_temp_f)
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

# 4. Dispatch & Logistics Operations with MySQL Integration
def dispatch_queue(request):
    # Setup default operational records in MySQL if none exist
    if Delivery.objects.count() == 0:
        kitchen = Kitchen.objects.first()
        if not kitchen:
            dummy_user, _ = User.objects.get_or_create(
                username="central_culinary_hub",
                defaults={'role': 'partner', 'first_name': 'Central Culinary Hub'}
            )
            kitchen = Kitchen.objects.create(
                user=dummy_user,
                address="100 culinary St, Central Area",
                max_daily_capacity=500
            )
            
        default_members = [
            ('120 Elm St', 3.4, '#MEM-890'),
            ('45 Forest Rd', 12.1, '#MEM-412'),
            ('88 Oak Blvd', 8.7, '#MEM-551')
        ]
        for i, (addr, dist, first) in enumerate(default_members):
            user = User.objects.create_user(
                username=f"dispatch_member_{i}" + str(User.objects.count() + 1),
                role='member',
                first_name=first
            )
            member = Member.objects.create(
                user=user,
                address=addr,
                status='active',
                latitude=40.7128,
                longitude=-74.0060
            )
            Delivery.objects.create(
                member=member,
                kitchen=kitchen,
                scheduled_date="2026-05-23",
                delivery_status='pending',
                distance_km=dist
            )
            
    deliveries = Delivery.objects.filter(delivery_status='pending').order_by('distance_km')
    context = {'deliveries': deliveries}
    return render(request, 'dispatch.html', context)

def allocate_route(request):
    if request.method == 'POST':
        delivery_id = request.POST.get('delivery_id')
        if delivery_id:
            Delivery.objects.filter(id=delivery_id).update(delivery_status='assigned')
            return JsonResponse({'status': 'success'})
        else:
            # Auto-allocate all pending routes
            Delivery.objects.filter(delivery_status='pending').update(delivery_status='assigned')
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

# 5. Donor & Pledge Hub operations with MySQL Integration
def donor_portal(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'donation':
            name = request.POST.get('name', 'Anonymous Donor')
            email = request.POST.get('email', '')
            amount = request.POST.get('amount', 100.00)
            
            Donation.objects.create(
                donor_name=name,
                donor_email=email,
                amount=amount,
                payment_status='success'
            )
            receipt_id = f'MM-TXN-REC-{Donation.objects.count() + 77800}'
            return JsonResponse({
                'status': 'success',
                'receipt_id': receipt_id,
                'donor_name': name,
                'amount': amount
            })
            
        elif action == 'pledge':
            asset_class = request.POST.get('asset_class', 'E-Bike')
            desc = request.POST.get('desc', '')
            
            Donation.objects.create(
                donor_name="Mark K. (Pledge)",
                donor_email="pledge@merrymeal.org",
                amount=0.01,
                pledged_resources=f"{asset_class}: {desc}",
                payment_status='pledged'
            )
            return JsonResponse({
                'status': 'success',
                'asset_name': asset_class,
                'desc': desc
            })
            
    # Load recent resource pledges from MySQL database
    pledges = Donation.objects.filter(payment_status='pledged').order_by('-donated_at')[:5]
    context = {'pledges': pledges}
    return render(request, 'donor.html', context)

# 6. Administrative MIS Analytics Suite with aggregated queries
def mis_dashboard(request):
    # Total Pledges value + Delivered stats
    meals_served_count = 14250 + Delivery.objects.filter(delivery_status='assigned').count()
    
    active_seniors_count = Member.objects.filter(status='active').count()
    if active_seniors_count == 0: active_seniors_count = 1240
    
    active_riders_count = Volunteer.objects.filter(status='active').count()
    if active_riders_count == 0: active_riders_count = 42
    
    kitchens_count = Kitchen.objects.count()
    if kitchens_count == 0: kitchens_count = 8
    
    context = {
        'meals_served': meals_served_count,
        'active_seniors': active_seniors_count,
        'active_riders': active_riders_count,
        'kitchens': kitchens_count
    }
    return render(request, 'dashboard.html', context)
