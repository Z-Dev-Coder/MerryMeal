from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.models import User, Member, Caregiver, Volunteer, Kitchen, FoodSafetyLog, Delivery, Donation
from core.services.geo_service import GeoService
import random
from django.core.mail import send_mail

# 1. Public Homepage View
def home(request):
    return render(request, 'home.html')

# 2. Onboarding & Authentication with Consolidated MySQL Senior Member Flow
def register(request):
    role = request.GET.get('role', 'member')
    tab = request.GET.get('tab', 'register')
    
    if request.method == 'POST':
        form_role = request.POST.get('role')
        
        if form_role == 'member':
            name = request.POST.get('memberName', 'Anonymous Member')
            phone = request.POST.get('memberPhone', '')
            email = request.POST.get('memberEmail', '')
            address = request.POST.get('memberAddress', '')
            password = request.POST.get('memberPassword', 'MerryMeal123!')
            
            # Retrieve checkboxes + custom text for dietary profile
            diets_selected = request.POST.getlist('dietary_needs')
            custom_allergies = request.POST.get('memberAllergies', '')
            
            diet_summary = ""
            if diets_selected:
                diet_summary += "Medically Tailored: " + ", ".join(diets_selected)
            if custom_allergies:
                if diet_summary:
                    diet_summary += " | "
                diet_summary += "Custom Allergies: " + custom_allergies
            if not diet_summary:
                diet_summary = "None Declared"
                
            # Emergency Contact
            emergency_contact = request.POST.get('emergencyContact', '')
            
            # Caregiver Details
            has_caregiver = request.POST.get('hasCaregiver') == 'yes'
            caregiver_name = request.POST.get('caregiverName', '')
            caregiver_phone = request.POST.get('caregiverPhone', '')
            caregiver_email = request.POST.get('caregiverEmail', '')
            caregiver_relation = request.POST.get('caregiverRelation', 'spouse')

            # Ensure unique username in database
            base_username = name.lower().replace(' ', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                
            # Create Custom User record
            user = User.objects.create_user(
                username=username,
                phone=phone,
                email=email,
                role='member',
                first_name=name,
                password=password
            )
            
            # Geofencing Computation using GeoService
            active_regions = ["central area", "downtown district", "green valley", "west end", "elm st", "main st", "broadway", "bangkok", "krung thep", "bangkapi", "thon buri", "sukhumvit", "chatuchak"]
            in_coverage = any(region in address.lower() for region in active_regions)
            
            # Retrieve real coordinates from form if submitted, otherwise fallback to Bangkok base coordinates
            form_lat = request.POST.get('memberLatitude')
            form_lon = request.POST.get('memberLongitude')
            
            mock_dest_lat = None
            mock_dest_lon = None
            
            if form_lat and form_lon:
                try:
                    mock_dest_lat = float(form_lat)
                    mock_dest_lon = float(form_lon)
                except ValueError:
                    pass
                    
            if mock_dest_lat is None or mock_dest_lon is None:
                # Bangkok Base coordinate fallback with deterministic offset based on address length
                mock_origin_lat = 13.7563
                mock_origin_lon = 100.5018
                coord_offset = (len(address) % 50) * 0.005
                mock_dest_lat = mock_origin_lat + coord_offset
                mock_dest_lon = mock_origin_lon + coord_offset
            
            # Load active kitchens list (equivalent to active_kitchens view)
            kitchens = Kitchen.objects.all()
            hubs = []
            for k in kitchens:
                if k.latitude and k.longitude:
                    hubs.append({
                        'name': f"MerryMeal Kitchen - {k.user.first_name}",
                        'latitude': float(k.latitude),
                        'longitude': float(k.longitude),
                    })
            if not hubs:
                hubs = [
                    {'name': 'MerryMeal Hub - Bangkapi (Central)', 'latitude': 13.7650, 'longitude': 100.6430},
                    {'name': 'MerryMeal Hub - Chatuchak (North)', 'latitude': 13.8030, 'longitude': 100.5530},
                    {'name': 'MerryMeal Hub - Sukhumvit (South)', 'latitude': 13.7360, 'longitude': 100.5600}
                ]
                
            # Find closest hub and calculate distance using GeoService
            min_distance = 99999.9
            for h in hubs:
                dist = GeoService.calculate_distance(mock_dest_lat, mock_dest_lon, h['latitude'], h['longitude'])
                if dist < min_distance:
                    min_distance = dist
                    
            distance = min_distance
            service_type = 'hot_meal' if distance < 10.0 else 'frozen_meal'
            
            if not in_coverage:
                if diet_summary == "None Declared" or not diet_summary:
                    diet_summary = "Expansion Waitlist Profile"
                else:
                    diet_summary += " | [Expansion Waitlist Profile]"
                service_type = 'frozen_meal'
            elif distance > 15.0:
                if diet_summary == "None Declared" or not diet_summary:
                    diet_summary = "[Exceeds 15km Safe Limit - Out-of-Range Reassessment]"
                else:
                    diet_summary += " | [Exceeds 15km Safe Limit - Out-of-Range Reassessment]"

            # Determine initial status: Out of coverage profiles bypass review and go straight to waitlist
            initial_status = 'waitlist' if not in_coverage else 'pending_reassessment'

            # Create Member profile
            member = Member.objects.create(
                user=user,
                address=address,
                latitude=mock_dest_lat,
                longitude=mock_dest_lon,
                dietary_restrictions=diet_summary,
                service_type=service_type,
                status=initial_status
            )
            
            # Create caregiver if provided
            caregiver_msg = ""
            if has_caregiver and caregiver_name and caregiver_phone:
                cg_username = caregiver_name.lower().replace(' ', '_')
                cg_counter = 1
                while User.objects.filter(username=cg_username).exists():
                    cg_username = f"{caregiver_name.lower().replace(' ', '_')}_{cg_counter}"
                    cg_counter += 1
                    
                cg_user = User.objects.create_user(
                    username=cg_username,
                    phone=caregiver_phone,
                    email=caregiver_email,
                    role='caregiver',
                    first_name=caregiver_name
                )
                Caregiver.objects.create(
                    user=cg_user,
                    associated_member=member,
                    relationship=caregiver_relation
                )
                caregiver_msg = f" Caregiver profile for {caregiver_name} has been linked with verification pending."

            if not in_coverage:
                eligibility_str = "Address is outside active zones. Automatically placed on Expansion Waitlist."
            elif distance > 15.0:
                eligibility_str = f"Calculated distance ({distance}km) exceeds the 15km safety limit. Flagged for out-of-range coordinator manual safety reassessment."
            else:
                eligibility_str = f"Qualified for daily hot meals (distance: {distance}km < 10km)." if service_type == 'hot_meal' else f"Assigned to weekend frozen meals (distance: {distance}km >= 10km)."

            # Generate onboarding Verification OTP code
            otp_code = str(random.randint(100000, 999999))
            
            # Send waitlist notification email immediately if out of coverage
            if not in_coverage and email:
                try:
                    html_message = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                    </head>
                    <body style="font-family: sans-serif; color: #333333; margin: 0; padding: 20px;">
                        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                            <div style="text-align: center; margin-bottom: 20px;">
                                <span style="font-size: 24px; font-weight: bold; color: #f97316;">🍊 MerryMeal Program</span>
                            </div>
                            <h2 style="color: #0f172a; margin-top: 0;">Hello {name},</h2>
                            <p style="font-size: 16px; line-height: 1.6; color: #475569;">
                                Thank you for applying to join the <strong>MerryMeal Senior Nutrition Program</strong>.
                            </p>
                            <p style="font-size: 16px; line-height: 1.6; color: #475569;">
                                Our automated geofencing check indicates that your address is currently <strong>outside our active pilot coverage districts</strong> in Bangkok.
                            </p>
                            
                            <div style="background-color: #fff7ed; border: 1px solid #ffedd5; border-radius: 6px; padding: 15px; margin: 20px 0;">
                                <h4 style="margin-top: 0; margin-bottom: 5px; color: #ea580c; font-weight: bold;">Saved directly to Expansion Waitlist:</h4>
                                <p style="margin: 0; font-size: 14px; color: #c2410c; line-height: 1.5;">
                                    We have logged your application directly into our <strong>Expansion Waitlist Queue (Status: Waitlist)</strong>. You do not need to take any action. Our staff will notify you immediately once service boundaries expand to cover your residential perimeter.
                                </p>
                            </div>
                            
                            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                            <p style="font-size: 12px; color: #94a3b8; text-align: center; margin-bottom: 0;">
                                MerryMeal Senior Nutrition Program &copy; 2026. All rights reserved.
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    plain_message = f"Hello {name},\n\nThank you for applying to the MerryMeal Senior Nutrition Program.\n\nOur geofencing review indicates that your address is currently outside our active pilot coverage areas in Bangkok.\n\nWe have saved your profile directly to our Expansion Waitlist Queue (Status: Waitlist). We will notify you immediately once service boundaries expand to your district!\n\nWarm regards,\nMerryMeal Operations Desk"
                    
                    send_mail(
                        subject="MerryMeal Program - Expansion Waitlist Staged",
                        message=plain_message,
                        from_email="onboarding@merrymeal.org",
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=True
                    )
                    print(f"[ONBOARDING MAIL SERVICE] Out of coverage waitlist notification sent to {email}")
                except Exception as e:
                    print(f"Error sending waitlist email: {e}")

            # Log credentials dispatch locally to backend server console (simulate mail server staging)
            if in_coverage:
                print(f"[ONBOARDING MAIL SERVICE] Queued profile for {name} ({email}). Awaiting coordinator review approval.")

            return JsonResponse({
                'status': 'success', 
                'otp_code': otp_code,
                'username': username,
                'email': email,
                'name': name,
                'in_coverage': in_coverage,
                'message': f'Member application for {name} logged successfully! {eligibility_str}{caregiver_msg} Your account is placed in the Operational Review Pipeline.' if in_coverage else f'Member application for {name} saved directly to the waitlist queue! Address is outside our current active zones.'
            })
            
        else:
            # Consolidates all brainstorming role submissions
            role_title = form_role.capitalize() if form_role else 'Stakeholder'
            return JsonResponse({
                'status': 'success',
                'message': f'Interactive brainstorming response for {role_title} received! Operational staff has queued this specialization for layout validation and roadmap checks.'
            })

    context = {'active_role': role, 'active_tab': tab}
    return render(request, 'register.html', context)

def user_login(request):
    return redirect('home')

def user_logout(request):
    logout(request)
    return redirect('home')

# 3. Kitchen Dashboard - Restored to high-fidelity mockup view
def kitchen_dashboard(request):
    return render(request, 'kitchen.html')

def safety_log_post(request):
    return JsonResponse({'status': 'success', 'message': 'HACCP Safety Log Staged (Mock Mode)'})

# 4. Dispatch & Logistics - Restored to high-fidelity mockup view
def dispatch_queue(request):
    return render(request, 'dispatch.html')

def allocate_route(request):
    return JsonResponse({'status': 'success', 'message': 'Routing Allocations Staged (Mock Mode)'})

# 5. Donor & Pledge Hub - Restored to high-fidelity mockup view
def donor_portal(request):
    return render(request, 'donor.html')

# 6. Administrative MIS Suite - Restored to high-fidelity mockup view
def mis_dashboard(request):
    return render(request, 'dashboard.html')

def active_kitchens(request):
    kitchens = Kitchen.objects.all()
    data = []
    for k in kitchens:
        data.append({
            'name': f"MerryMeal Kitchen - {k.user.first_name}",
            'address': k.address,
            'latitude': float(k.latitude) if k.latitude else 0.0,
            'longitude': float(k.longitude) if k.longitude else 0.0,
        })
    
    # If no real kitchens are registered in MySQL yet, seed/return our 3 mock Bangkok pilot kitchens
    if not data:
        data = [
            {
                'name': 'MerryMeal Hub - Bangkapi (Central)',
                'address': 'The Mall Bangkapi, Lat Phrao Rd, Bangkok',
                'latitude': 13.7650,
                'longitude': 100.6430
            },
            {
                'name': 'MerryMeal Hub - Chatuchak (North)',
                'address': 'Central Ladprao, Phahonyothin Rd, Bangkok',
                'latitude': 13.8030,
                'longitude': 100.5530
            },
            {
                'name': 'MerryMeal Hub - Sukhumvit (South)',
                'address': 'Asok Intersection, Sukhumvit Rd, Bangkok',
                'latitude': 13.7360,
                'longitude': 100.5600
            }
        ]
    return JsonResponse({'status': 'success', 'kitchens': data})

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def approve_simulated_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
        
        name = data.get('name', 'Anonymous Member')
        email = data.get('email', '')
        username = data.get('username', '')
        
        if email:
            try:
                html_message = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                </head>
                <body style="font-family: sans-serif; color: #333333; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <span style="font-size: 24px; font-weight: bold; color: #0284c7;">✨ MerryMeal Onboarding</span>
                        </div>
                        <h2 style="color: #0f172a; margin-top: 0;">Hello {name},</h2>
                        <p style="font-size: 16px; line-height: 1.6; color: #475569;">
                            We are pleased to inform you that your application for the <strong>MerryMeal Senior Nutrition Program</strong> has been approved by our staff!
                        </p>
                        <p style="font-size: 16px; line-height: 1.6; color: #475569;">
                            You can now log in to your dashboard to manage your meals, schedule caregiver links, and track deliveries.
                        </p>
                        
                        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; margin: 20px 0;">
                            <h4 style="margin-top: 0; margin-bottom: 10px; color: #0f172a; font-weight: bold;">Your Secure Portal Credentials:</h4>
                            <table style="width: 100%; border-collapse: collapse; font-size: 15px;">
                                <tr>
                                    <td style="padding: 4px 0; color: #64748b; width: 100px;">Username:</td>
                                    <td style="padding: 4px 0; font-weight: bold; color: #0f172a;">{username}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 4px 0; color: #64748b;">Password:</td>
                                    <td style="padding: 4px 0; font-weight: bold; color: #0f172a;">MerryMeal123!</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://127.0.0.1:8000/login/" style="display: inline-block; background-color: #0284c7; color: #ffffff; padding: 14px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(2, 132, 199, 0.2); transition: background-color 0.2s ease;">
                                Login to Dashboard
                            </a>
                        </div>
                        
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                        <p style="font-size: 12px; color: #94a3b8; text-align: center; margin-bottom: 0;">
                            MerryMeal Senior Nutrition Program &copy; 2026. All rights reserved.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                plain_message = f"Hello {name},\n\nWe are pleased to inform you that your application for the MerryMeal Senior Nutrition Program has been approved by our staff!\n\nYou can now log in to your dashboard to manage your meals, schedule caregiver links, and track deliveries.\n\nYour secure portal credentials are:\n👉 Username: {username}\n👉 Temporary Password: MerryMeal123!\n\nPlease log in here: http://127.0.0.1:8000/login/\n\nWarm regards,\nMerryMeal Operations Desk"
                
                send_mail(
                    subject="MerryMeal Onboarding - Account Approved!",
                    message=plain_message,
                    from_email="onboarding@merrymeal.org",
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=True
                )
                print(f"[ONBOARDING MAIL SERVICE] Simulated credentials email successfully dispatched to {email}")
            except Exception as e:
                print(f"Error sending simulated approval email: {e}")
                
        return JsonResponse({'status': 'success', 'message': 'Simulated review approved, credentials email dispatched.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
