# System Technical Specification: Django Meals on Wheels (MerryMeal)

This document contains the complete technical specifications, database schema ORM classes, Python-side services, and accessibility check-sheets for the **Unified Meals on Wheels Web Application** in Python/Django.

---

## 1. Database Schema Blueprint (Django ORM Models)

We will use Django's robust Object-Relational Mapper (ORM) to define our database models. These classes will automatically compile into MySQL tables with proper index optimizations, relational integrity, and checks.

```python
# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# 1. Custom User Model supporting role separation
class User(AbstractUser):
    ROLE_CHOICES = [
        ('member', 'Senior Member'),
        ('caregiver', 'Caregiver'),
        ('volunteer', 'Volunteer Rider'),
        ('partner', 'Outsourced Kitchen Partner'),
        ('admin', 'MerryMeal Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    phone = models.CharField(max_length=20, blank=False)

    class Meta:
        db_table = 'users'

# 2. Member Profile (A11y requirements & GIS distance mapping)
class Member(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending_reassessment', 'Pending Reassessment'),
    ]
    SERVICE_CHOICES = [
        ('hot_meal', 'Hot Noon Meal (M-F)'),
        ('frozen_meal', 'Frozen Meal (Weekend Support)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    address = models.CharField(max_length=255, blank=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    dietary_restrictions = models.TextField(null=True, blank=True, help_text="Common allergies and medical diets list")
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='hot_meal')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='active')
    last_assessment_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'members'
        indexes = [models.Index(fields=['status'])]

# 3. Caregiver Profile and Dependent Link
class Caregiver(models.Model):
    RELATION_CHOICES = [
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('professional', 'Professional Caregiver'),
        ('neighbor', 'Neighbor'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='caregiver_profile')
    associated_member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='caregivers')
    relationship = models.CharField(max_length=50, choices=RELATION_CHOICES)

    class Meta:
        db_table = 'caregivers'

# 4. Volunteer Rider Configuration
class Volunteer(models.Model):
    VEHICLE_CHOICES = [
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('walk', 'Walk/Foot'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='car')
    availability_schedule = models.CharField(max_length=255, help_text="Comma-separated operating days")
    operating_radius_km = models.DecimalField(max_digits=4, decimal_places=2, default=10.00)
    status = models.CharField(max_length=20, default='active')

    class Meta:
        db_table = 'volunteers'
        indexes = [models.Index(fields=['status'])]

# 5. Partner Kitchen Facility Model
class Kitchen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kitchen_profile')
    address = models.CharField(max_length=255, blank=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    max_daily_capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'kitchens'

# 6. Back-of-House Ingredient Inventory
class InventoryItem(models.Model):
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='inventory')
    item_name = models.CharField(max_length=150)
    quantity_kg = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    expiration_date = models.DateField()

    class Meta:
        db_table = 'inventory'
        indexes = [models.Index(fields=['expiration_date'])]

# 7. Dynamic Cooking Safety Temp Logs
class FoodSafetyLog(models.Model):
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='safety_logs')
    dish_name = models.CharField(max_length=150)
    portion_count = models.PositiveIntegerField()
    cooking_temp_f = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(165.0)])
    holding_temp_f = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(140.0)])
    logged_at = models.DateTimeField(auto_now_add=True)
    kitchen_staff_signoff = models.CharField(max_length=100)

    class Meta:
        db_table = 'food_safety_logs'

# 8. GIS Dispatch Deliveries Routing Ledger
class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Allocation'),
        ('assigned', 'Assigned Driver'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='deliveries')
    volunteer = models.ForeignKey(Volunteer, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='deliveries')
    scheduled_date = models.DateField()
    delivery_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    proof_photo_url = models.CharField(max_length=255, null=True, blank=True)
    receiver_signature = models.CharField(max_length=255, null=True, blank=True)
    wellness_remarks = models.TextField(null=True, blank=True)
    feedback_rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback_comments = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'deliveries'
        indexes = [models.Index(fields=['scheduled_date', 'delivery_status'])]

# 9. Need Reassessments Schedules
class Reassessment(models.Model):
    STATUS_CHOICES = [
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
        ('requires_review', 'Requires Review'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reassessments')
    audit_date = models.DateField()
    social_worker_name = models.CharField(max_length=100)
    eligibility_status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    assessment_notes = models.TextField()

    class Meta:
        db_table = 'reassessments'

# 10. Financial Donations
class Donation(models.Model):
    donor_name = models.CharField(max_length=100)
    donor_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_status = models.CharField(max_length=20, default='success')
    pledged_resources = models.TextField(null=True, blank=True)
    donated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'donations'
```

---

## 2. Dynamic Views & Routing Table (Django Views)

The backend handles routes using Python methods inside `core/views.py`:

| URL Pattern | View Function | Method | DTL Template | Description |
|---|---|---|---|---|
| `/` | `views.home` | GET | `base.html` | Public landing page. |
| `/register/` | `views.register` | GET, POST | `register.html` | Unified registration forms with accessibility configs. |
| `/login/` | `views.user_login` | GET, POST | `register.html` | Core role authentication check. |
| `/logout/` | `views.user_logout` | GET | - | Terminate active user session. |
| `/kitchen/dashboard/` | `views.kitchen_dashboard` | GET | `kitchen.html` | Kitchen portion scaling, stock checklist & expiry. |
| `/kitchen/safety-log/` | `views.safety_log_post` | POST | - | Log food temperatures. Locks active delivery logs. |
| `/dispatch/queue/` | `views.dispatch_queue` | GET | `dispatch.html` | Dispatch map overlays, 10km radius checks, sequencing. |
| `/dispatch/allocate/` | `views.allocate_route` | POST | - | Auto-sequence pending deliveries to volunteer riders. |
| `/donor/portal/` | `views.donor_portal` | GET, POST | `donor.html` | Process card mock transactions and supporter resource pledges. |
| `/admin/mis/dashboard/` | `views.mis_dashboard` | GET | `dashboard.html` | Executive MIS dashboard with tracking parameters. |

---

## 3. Geospatial & Payments Python Services

To decouple dependencies, we implement service abstraction classes in Python.

### A. Geolocation & Distance Calculation (`core/services/geo_service.py`)
Calculates driving distance using the Haversine spherical math models:

```python
# core/services/geo_service.py
import math

class GeoService:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Compute Great-Circle Distance using Haversine formula
        """
        if not lat1 or not lon1 or not lat2 or not lon2:
            return 0.0
            
        R = 6371.0 # Earth's radius in kilometers
        
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        
        delta_phi = math.radians(float(lat2) - float(lat1))
        delta_lambda = math.radians(float(lon2) - float(lon1))
        
        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             (math.sin(delta_lambda / 2.0) ** 2))
             
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c # Distance in km

    @classmethod
    def get_route_details(cls, origin_lat, origin_lon, dest_lat, dest_lon, live_mode=False):
        """
        Calculates details. Toggles to Google Maps SDK if live_mode is enabled.
        """
        if not live_mode:
            distance = cls.calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
            return {
                'distance_km': round(distance, 2),
                'duration_min': math.ceil(distance * 2.5), # Estimated travel time
                'is_hot_meal_eligible': distance < 10.0
            }
        else:
            # Placeholder for Google Maps API client execution
            pass
```

### B. Secure Payments Abstraction (`core/services/payment_service.py`)
```python
# core/services/payment_service.py
class PaymentService:
    @staticmethod
    def process_charge(amount_decimal, card_details, live_mode=False):
        """
        Toggles mock payment processor and active Stripe SDK API calls
        """
        if not live_mode:
            # Mock check: Simulate success if credit card has 16 digits
            card_num = str(card_details.get('card_number', '')).replace(' ', '')
            if len(card_num) == 16:
                return {'success': True, 'receipt_id': 'MOCK-TXN-12345'}
            return {'success': False, 'error': 'Invalid Card Length'}
        else:
            # Placeholder for actual Stripe Charge client SDK:
            # import stripe; stripe.Charge.create(...)
            pass
```

---

## 4. Accessibility (A11y) & Visual Integration Specs

To follow professional standards, we will implement these frontend UI/UX rules:

1.  **Accessibility Variables**: Custom typography sizing, spacing, and contrast settings are managed via custom variables inside `public/static/css/style.css`.
    ```css
    :root {
        --text-base-font: 'Outfit', sans-serif;
        --contrast-border: 1.5px solid transparent;
        /* Standard accessible light/dark parameters */
        --bg-primary: #ffffff;
        --text-primary: #1e293b;
    }
    
    /* Enabled via global visual widget */
    .high-contrast-mode {
        --bg-primary: #000000;
        --text-primary: #ffff00;
        --contrast-border: 2px solid #ffff00;
    }
    ```
2.  **HTML Heading Structure**: Each DTL template must strictly contain exactly **one primary `<h1>`** heading at the top of the body frame. All secondary headings must sequence down hierarchically (`<h2>`, `<h3>`).
3.  **Bootstrap 5 Visual Integration**: Onboarding forms are arranged in structured grid divisions (`col-12 col-md-8 offset-md-2`). Large interactive buttons must feature hover and focus outlines:
    ```css
    .a11y-btn:focus {
        outline: 3px solid #f59e0b !important;
        outline-offset: 2px;
    }
    ```
4.  **Touch-Target Limits**: Tap components (navigation items, role tabs, and checklist fields) must feature a minimum height and width profile of **48px x 48px** to remain accessible for elderly and motor-impaired individuals.

---

## 5. Agile Development & Collaboration Protocol

To ensure full user alignment and avoid isolated architectural assumptions, the following protocol applies to every feature, module, and view:
1.  **Layout Brainstorming First**: The developer **must not** build any template layout (e.g., top navigation bars, middle hero banner segments, footers, card grids, split columns) in isolation.
2.  **Collaborative Definition**: Before writing code, the developer must brainstorm and review with the user:
    *   **Content Strategy**: The specific headings, descriptive text, CTA links, and media elements in each layout zone.
    *   **Visual Geometry**: The structural layout format (e.g., side-by-side grids, responsive card containers, full-bleed backgrounds, or modular sections).
    *   **User Journeys**: Transition states, tab behaviors, modal sequences, and mobile reflow grids.
3.  **Documentation Anchoring**: This constraint is permanently recorded as the core system implementation directive.
