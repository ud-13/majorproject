from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('home_owner', 'Home Owner'),
        ('police', 'Police'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Tenant(models.Model):
    PROFESSION_CHOICES = [
        ('Government Servant', 'Government Servant'),
        ('Public Sector Undertaking Employee', 'Public Sector Undertaking Employee'),
        ('Retired Government Servant', 'Retired Government Servant'),
        ('Retired PSU Employee', 'Retired PSU Employee'),
        ('Businessman/Self-Employed', 'Businessman/Self-Employed'),
        ('Private Employee', 'Private Employee'),
        ('Others', 'Others'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    POLICE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    DISTRICT_CHOICES = [
        ('Gangtok', 'Gangtok'),
        ('Mangan', 'Mangan'),
        ('Pakyong', 'Pakyong'),
        ('Soreng', 'Soreng'),
        ('Namchi', 'Namchi'),
        ('Gyalshing', 'Gyalshing'),
    ]

    # User relationship
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenants'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField(blank=True, null=True)
    photo = models.ImageField(upload_to='tenant_photos/')
    father_name = models.CharField(max_length=100)
    tenant_phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')]
    )
   
    # Address Information
    permanent_address = models.TextField()
    village = models.CharField(max_length=100)
    tehsil = models.CharField(max_length=100)
    post_office = models.CharField(max_length=100)
    pin_code = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit pin code')]
    )
    police_station = models.CharField(max_length=100)
    district = models.CharField(max_length=100, choices=DISTRICT_CHOICES)
    owner_phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')]
    )
    
    # Professional Information
    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES)
    other_profession = models.CharField(max_length=100, blank=True, null=True)
    
    # Employment Status (changed from BooleanField to CharField to match form)
    serving_employee = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        default='No'
    )
    serving_certificate = models.FileField(
        upload_to='certificates/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    retired_employee = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        default='No'
    )
    retired_certificate = models.FileField(
        upload_to='certificates/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    # Sikkim Certificate (changed from BooleanField to CharField to match form)
    sikkim_certificate = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        default='No'
    )
    sikkim_certificate_file = models.FileField(
        upload_to='certificates/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    # Additional Information
    previous_police_station = models.CharField(max_length=100, blank=True, null=True)
    
    # Signature
    signature_date = models.DateField()
    signature = models.ImageField(
        upload_to='signatures/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    
    # Status Fields
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    police_status = models.CharField(max_length=10, choices=POLICE_STATUS_CHOICES, default='pending')
    police_remark = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        errors = {}
        
        if self.profession == 'Others' and not self.other_profession:
            errors['other_profession'] = "Please specify your profession"
        
        if self.serving_employee == 'Yes' and not self.serving_certificate:
            errors['serving_certificate'] = "Please upload a certificate if you are a serving employee"
        
        if self.retired_employee == 'Yes' and not self.retired_certificate:
            errors['retired_certificate'] = "Please upload a certificate if you are a retired employee"
        
        if self.sikkim_certificate == 'Yes' and not self.sikkim_certificate_file:
            errors['sikkim_certificate_file'] = "Please upload a certificate if you hold a Sikkim certificate"
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['-created_at']


class FamilyMember(models.Model):
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='family_members'
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField(blank=True, null=True)
    relationship = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.relationship})"

    class Meta:
        verbose_name = 'Family Member'
        verbose_name_plural = 'Family Members'
        ordering = ['tenant', 'relationship']


class PreviousResidence(models.Model):
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='Tenant_previousresidence'
    )
    from_place = models.CharField(max_length=100)
    to_place = models.CharField(max_length=100)
    address = models.TextField()
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_place} to {self.to_place}"

    class Meta:
        verbose_name = 'Previous Residence'
        verbose_name_plural = 'Previous Residences'
        ordering = ['tenant', '-created_at']


class HomeOwner(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='homeowner_profile'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField(blank=True, null=True)
    photo = models.ImageField(upload_to='homeowner_photos/')
    
    # Contact Information
    phone = models.CharField(
        max_length=15, 
        validators=[RegexValidator(r'^\d{10,15}$', 'Enter a valid phone number')]
    )
    
    # Document Information
    aadhar_card = models.FileField(
        upload_to='aadhar_cards/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    aadhar_number = models.CharField(
        max_length=12, 
        validators=[RegexValidator(r'^\d{12}$', 'Enter a valid 12-digit Aadhar number')]
    )
    sikkim_certificate = models.FileField(
        upload_to='sikkim_certificates/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    residential_certificate = models.FileField(
        upload_to='residential_certificates/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    land_parcha = models.FileField(
        upload_to='land_parchas/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Home Owner'
        verbose_name_plural = 'Home Owners'
        ordering = ['-created_at']