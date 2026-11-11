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
        ('waitlist', 'Expansion Waitlist'),
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
