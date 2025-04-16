from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .models import Tenant, FamilyMember, PreviousResidence, HomeOwner
from .forms import HomeOwnerForm
import random
import re
import os
from datetime import datetime
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.db import transaction
import logging
User = get_user_model()

logger = logging.getLogger(__name__)

# Login view remains the same
def login(request):
    return render(request, 'login.html')

def index(request):
    role = request.GET.get('role', 'tenant')
    context = {'role': role}
    return render(request, 'index.html', context)

def SignUpPolice(request):
    return render(request, 'SignUpPolice.html')

def ApplicationStatus(request):
    return render(request, 'ApplicationStatus.html')

def HomeOwnerdashboard(request):
    return render(request, 'HomeOwnerdashboard.html')


def Policedashboard(request):
    tenants = Tenant.objects.filter(status='Approved', police_status='Pending')
    return render(request, 'Policedashboard.html', {'tenants': tenants})


def police_approve_tenant(request, tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)
    if request.method == 'POST':
        tenant.police_status = 'Approved'
        tenant.save()
        send_mail(
            'Tenant Verification Approved',
            'Dear tenant, your verification has been successfully approved by the police.',
            settings.DEFAULT_FROM_EMAIL,
            [tenant.email],
            fail_silently=False,
        )
        return redirect('police_dashboard')
    return render(request, 'Policedashboard.html')


def police_reject_tenant(request, tenant_id):
    tenant = Tenant.objects.get(id=tenant_id)
    if request.method == 'POST':
        remark = request.POST.get('remark')
        tenant.police_status = 'Rejected'
        tenant.police_remark = remark
        tenant.save()
        return redirect('police_dashboard')
    return render(request, 'Policedashboard.html')




@login_required
def check_verification(request):
    return JsonResponse({
        'verified': True,
        'email': request.user.email
    })

@csrf_exempt
def Registration(request):
    if request.method == 'GET':
        if not request.session.get('verified_email'):
            return redirect('login')
        return render(request, 'Registration.html')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                verified_email = request.session.get('verified_email')
                if not verified_email:
                    return JsonResponse({
                        'success': False,
                        'error':  "Please verify your email first. Check your inbox!",
                        'redirect_url': reverse('/login')
                    }, status=403)

                user = request.user
                fname = request.POST.get("first_name")
                print(user)
            logger.error(f"user is fetched{user}{fname}")
            
            # Handle file uploads
            def handle_upload(file_field, upload_to):
                if file_field in request.FILES:
                    fs = FileSystemStorage(location=f'media/{upload_to}')
                    filename = fs.save(request.FILES[file_field].name, request.FILES[file_field])
                    return f'{upload_to}/{filename}'
                return None

            # Validate and prepare tenant data
            tenant_data = {
                'user': user,
                'first_name': request.POST.get('first_name', '').strip(),
                'middle_name': request.POST.get('middle_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'date_of_birth': request.POST.get('date_of_birth'),
                'age': request.POST.get('age'),
                'photo': handle_upload('photo', 'tenant_photos'),
                'father_name': request.POST.get('father_name', '').strip(),
                'permanent_address': request.POST.get('permanent_address', '').strip(),
                'village': request.POST.get('village', '').strip(),
                'tehsil': request.POST.get('tehsil', '').strip(),
                'post_office': request.POST.get('post_office', '').strip(),
                'pin_code': request.POST.get('pin_code', '').strip(),
                'police_station': request.POST.get('police_station', '').strip(),
                'district': request.POST.get('district', 'Gangtok'),  
                'tenant_phone_number': request.POST.get('tenant_phone_number', '').strip(),
                'owner_phone_number': request.POST.get('owner_phone_number', '').strip(),
                'profession': request.POST.get('profession', 'Others'),
                'other_profession': request.POST.get('other_profession', '').strip(),
                'serving_employee': request.POST.get('serving_employee'),
                'serving_certificate': handle_upload('servingCertificate', 'certificates'),
                'retired_employee': request.POST.get('retired_employee'),
                'retired_certificate': handle_upload('retiredCertificate', 'certificates'),
                'sikkim_certificate': request.POST.get('sikkim_certificate'),
                'sikkim_certificate_file': handle_upload('sikkimCertificateFile', 'certificates'),
                'previous_police_station': request.POST.get('previous_police_station', '').strip(),
                'signature_date': request.POST.get('signature_date'),
                'signature': handle_upload('signature', 'signatures'),
                'status': 'pending',  
                'police_status': 'pending',  
            }
            logger.debug(f"tenantdata{tenant_data}")

            # Validate required fields
            required_fields = [
                'first_name', 'last_name', 'date_of_birth', 'father_name',
                'permanent_address', 'post_office', 'pin_code', 'police_station',
                'tenant_phone_number', 'owner_phone_number', 'signature_date',
                'signature'
            ]
            
            missing_fields = [field for field in required_fields if not tenant_data.get(field)]
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)

            # Handle age calculation if not provided
            if not tenant_data['age'] and tenant_data['date_of_birth']:
                try:
                    dob = datetime.strptime(tenant_data['date_of_birth'], '%Y-%m-%d').date()
                    today = timezone.now().date()
                    tenant_data['age'] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                except (ValueError, TypeError):
                    pass

            # Create tenant
            tenant = Tenant.objects.create(**tenant_data)
            
            # Process family members
            i = 0
            while f'family_members[{i}][first_name]' in request.POST:
                family_data = {
                    'tenant': tenant,
                    'first_name': request.POST.get(f'family_members[{i}][first_name]', '').strip(),
                    'middle_name': request.POST.get(f'family_members[{i}][middle_name]', '').strip(),
                    'last_name': request.POST.get(f'family_members[{i}][last_name]', '').strip(),
                    'date_of_birth': request.POST.get(f'family_members[{i}][dob]'),
                    'age': request.POST.get(f'family_members[{i}][age]'),
                    'relationship': request.POST.get(f'family_members[{i}][relationship]', '').strip(),
                    'profession': request.POST.get(f'family_members[{i}][profession]', '').strip(),
                }
                
                # Calculate age if not provided
                if not family_data['age'] and family_data['date_of_birth']:
                    try:
                        dob = datetime.strptime(family_data['date_of_birth'], '%Y-%m-%d').date()
                        today = timezone.now().date()
                        family_data['age'] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    except (ValueError, TypeError):
                        pass
                
                FamilyMember.objects.create(**family_data)
                i += 1

            # Process previous residences
            j = 0
            while f'Tenant_previousresidence[{j}][from_place]' in request.POST:
                PreviousResidence.objects.create(
                    tenant=tenant,
                    from_place=request.POST.get(f'Tenant_previousresidence[{j}][from_place]', '').strip(),
                    to_place=request.POST.get(f'Tenant_previousresidence[{j}][to_place]', '').strip(),
                    address=request.POST.get(f'Tenant_previousresidence[{j}][address]', '').strip()
                )
                j += 1

            # Clear session and show success
            if 'verified_email' in request.session:
                del request.session['verified_email']

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('ApplicationStatus')
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
        
def signup_homeowner(request):
    if request.method == 'POST':
        form = HomeOwnerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('HomeOwnerdashboard')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = HomeOwnerForm()
    return render(request, 'signup_homeowner.html', {'form': form})

def generate_otp():
    return str(random.randint(100000, 999999))

@csrf_exempt
def send_otp(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    email = request.POST.get('email')
    role = request.POST.get('role')
    
    if not email or not role:
        return JsonResponse({'success': False, 'error': 'Email and role are required'}, status=400)
    
    try:
        user, created = User.objects.get_or_create(email=email)
        user.role = role
        user.otp = generate_otp()
        user.otp_created_at = timezone.now()
        user.save()

        send_mail(
            'Your OTP Code',
            f'Your verification code is: {user.otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    email = request.POST.get('email', '').strip().lower()
    otp = request.POST.get('otp', '').strip()
    role = request.POST.get('role', 'tenant').strip().lower()
    
    if not email or not otp:
        return JsonResponse({'success': False, 'error': 'Email and OTP are required'}, status=400)
    
    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'role': role,
                'is_active': True
            }
        )
        
        # Verify OTP
        if not (user.otp and user.otp == otp):
            return JsonResponse({'success': False, 'error': 'Invalid OTP'}, status=400)
            
        # Check OTP expiration (5 minutes)
        if (timezone.now() - user.otp_created_at).total_seconds() > 300:
            return JsonResponse({'success': False, 'error': 'OTP has expired'}, status=400)
        
        # Log the user in - CORRECTED THIS LINE
        from django.contrib.auth import login as auth_login
        auth_login(request, user)
        
        # Store verification data in session
        request.session['verified_email'] = email
        request.session['verification_time'] = str(timezone.now())
        request.session['user_role'] = role
        request.session.modified = True
        
        # Determine redirect URL based on role
        redirect_url = reverse('Registration')
        if role == 'Home_owner':
            redirect_url = reverse('HomeOwnerRegistration')
        elif role == 'police':
            redirect_url = reverse('PoliceDashboard')
        
        return JsonResponse({
            'success': True,
            'redirect_url': redirect_url,
            'role': role
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    








    

