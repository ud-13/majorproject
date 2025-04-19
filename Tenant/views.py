from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, logout
from .models import Tenant, FamilyMember, PreviousResidence, HomeOwner
from .forms import HomeOwnerForm, TenantForm, FamilyMemberForm, PreviousResidenceForm
import random
import re
import os
from datetime import datetime
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.db import transaction
import logging
import json

User = get_user_model()

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def login(request):
    # Clear any existing session data
    if 'verified_email' in request.session:
        del request.session['verified_email']
    return render(request, 'login.html')

def new_login(request):
    # Clear any existing session data
    if 'verified_email' in request.session:
        del request.session['verified_email']
    return render(request, 'new_login.html')

def logout_view(request):
    logout(request)
    if 'verified_email' in request.session:
        del request.session['verified_email']
    return redirect('login')

def index(request):
    role = request.GET.get('role', 'tenant')
    context = {'role': role}
    return render(request, 'index.html', context)

def SignUpPolice(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Email is required')
            return render(request, 'SignUpPolice.html')

        # Create or get user with police role
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'role': 'police', 'is_active': True}
        )

        if not created:
            user.role = 'police'
            user.save()

        messages.success(request, 'Police account registered successfully')
        return redirect('login')

    return render(request, 'SignUpPolice.html')

def ApplicationStatus(request):
    tenants = []
    email = request.session.get('verified_email')

    if email:
        user = User.objects.filter(email=email).first()
        if user:
            tenants = Tenant.objects.filter(user=user)

    return render(request, 'ApplicationStatus.html', {'tenants': tenants})

def HomeOwnerdashboard(request):
    email = request.session.get('verified_email')
    if not email:
        messages.error(request, 'Please log in first')
        return redirect('login')

    user = User.objects.filter(email=email).first()
    if not user or user.role != 'home_owner':
        messages.error(request, 'Access denied. Please log in as a home owner.')
        return redirect('login')

    owner = HomeOwner.objects.filter(user=user).first()
    if not owner:
        messages.error(request, 'Please complete your profile first')
        return redirect('signup_homeowner')

    # Get all tenants who have this home owner's phone number, ordered by creation date
    tenants = Tenant.objects.filter(owner_phone_number=owner.phone).order_by('-created_at')

    return render(request, 'HomeOwnerdashboard.html', {
        'owner': owner,
        'tenants': tenants
    })

def approve_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    tenant.status = 'approved'
    tenant.save()
    messages.success(request, 'Tenant application approved successfully.')
    return redirect('HomeOwnerdashboard')

def reject_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    tenant.status = 'rejected'
    tenant.save()
    messages.success(request, 'Tenant application rejected.')
    return redirect('HomeOwnerdashboard')

def Policedashboard(request):
    # For police, show only approved tenants that need police verification
    tenants = Tenant.objects.filter(status='approved', police_status='pending')
    return render(request, 'Policedashboard.html', {'tenants': tenants})

def police_approve_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    if request.method == 'POST':
        tenant.police_status = 'approved'
        tenant.save()

        # Send notification email to tenant
        try:
            user = tenant.user
            send_mail(
                'Tenant Verification Approved',
                f'Dear {tenant.first_name} {tenant.last_name}, your verification has been successfully approved by the police.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Email error: {str(e)}")

        messages.success(request, f"Tenant {tenant.first_name} {tenant.last_name} approved successfully.")
        return redirect('Policedashboard')

    return render(request, 'Policedashboard.html', {'tenant': tenant})

def police_reject_tenant(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)

    if request.method == 'POST':
        remark = request.POST.get('remark', '')
        tenant.police_status = 'rejected'
        tenant.police_remark = remark
        tenant.save()

        # Send notification email to tenant
        try:
            user = tenant.user
            send_mail(
                'Tenant Verification Rejected',
                f'Dear {tenant.first_name} {tenant.last_name}, your verification has been rejected by the police. Reason: {remark}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Email error: {str(e)}")

        messages.success(request, f"Tenant {tenant.first_name} {tenant.last_name} rejected with remarks.")
        return redirect('Policedashboard')

    return render(request, 'Policedashboard.html', {'tenant': tenant})

@csrf_exempt
def check_verification(request):
    verified_email = request.session.get('verified_email')
    if verified_email:
        return JsonResponse({
            'verified': True,
            'email': verified_email
        })
    return JsonResponse({
        'verified': False
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
                # Get verified email from session
                verified_email = request.session.get('verified_email')
                if not verified_email:
                    return JsonResponse({
                        'success': False,
                        'error': "Please verify your email first. Check your inbox!",
                        'redirect_url': reverse('login')
                    }, status=403)

                # Get or create user
                user, created = User.objects.get_or_create(
                    email=verified_email,
                    defaults={'role': 'tenant', 'is_active': True}
                )

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
                    'serving_employee': request.POST.get('serving_employee', 'No'),
                    'serving_certificate': handle_upload('serving_certificate', 'certificates'),
                    'retired_employee': request.POST.get('retired_employee', 'No'),
                    'retired_certificate': handle_upload('retired_certificate', 'certificates'),
                    'sikkim_certificate': request.POST.get('sikkim_certificate', 'No'),
                    'sikkim_certificate_file': handle_upload('sikkim_certificate_file', 'certificates'),
                    'previous_police_station': request.POST.get('previous_police_station', '').strip(),
                    'signature_date': request.POST.get('signature_date'),
                    'signature': handle_upload('signature', 'signatures'),
                    'status': 'pending',  
                    'police_status': 'pending',  
                }

                # Log data for debugging
                logger.debug(f"Tenant data: {tenant_data}")

                # Validate required fields
                required_fields = [
                    'first_name', 'last_name', 'date_of_birth', 'father_name',
                    'permanent_address', 'post_office', 'pin_code', 'police_station',
                    'tenant_phone_number', 'owner_phone_number', 'signature_date'
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
                    except (ValueError, TypeError) as e:
                        logger.error(f"Date conversion error: {str(e)}")

                # Create tenant
                tenant = Tenant.objects.create(**tenant_data)

                # Process family members
                family_members_json = request.POST.get('family_members')
                if family_members_json:
                    try:
                        family_members_data = json.loads(family_members_json)
                        for fm_data in family_members_data:
                            family_data = {
                                'tenant': tenant,
                                'first_name': fm_data.get('first_name', '').strip(),
                                'middle_name': fm_data.get('middle_name', '').strip(),
                                'last_name': fm_data.get('last_name', '').strip(),
                                'date_of_birth': fm_data.get('dob'),
                                'age': fm_data.get('age'),
                                'relationship': fm_data.get('relationship', '').strip(),
                                'profession': fm_data.get('profession', '').strip(),
                            }

                            # Calculate age if not provided
                            if not family_data['age'] and family_data['date_of_birth']:
                                try:
                                    dob = datetime.strptime(family_data['date_of_birth'], '%Y-%m-%d').date()
                                    today = timezone.now().date()
                                    family_data['age'] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                                except (ValueError, TypeError) as e:
                                    logger.error(f"Family member date conversion error: {str(e)}")

                            FamilyMember.objects.create(**family_data)
                    except json.JSONDecodeError:
                        logger.error("Failed to parse family members JSON")

                # Process previous residences
                prev_residences_json = request.POST.get('previous_residences')
                if prev_residences_json:
                    try:
                        prev_residences_data = json.loads(prev_residences_json)
                        for pr_data in prev_residences_data:
                            PreviousResidence.objects.create(
                                tenant=tenant,
                                from_place=pr_data.get('from_place', '').strip(),
                                to_place=pr_data.get('to_place', '').strip(),
                                address=pr_data.get('address', '').strip()
                            )
                    except json.JSONDecodeError:
                        logger.error("Failed to parse previous residences JSON")

                # Clear session and show success
                if 'verified_email' in request.session:
                    del request.session['verified_email']

                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful',
                    'redirect_url': reverse('payment') + f'?tenant_id={tenant.id}'
                })

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

def signup_homeowner(request):
    if request.method == 'POST':
        email = request.session.get('verified_email')
        if not email:
            messages.error(request, 'Please verify your email first')
            return redirect('login')

        # Get existing user or create new one
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create(email=email, role='home_owner', is_active=True)
        elif user.role != 'home_owner':
            user.role = 'home_owner'
            user.save()

        # Handle form submission
        form = HomeOwnerForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create HomeOwner object
                home_owner = form.save(commit=False)
                home_owner.user = user

                # Calculate age if not provided
                if not home_owner.age and home_owner.date_of_birth:
                    today = timezone.now().date()
                    home_owner.age = today.year - home_owner.date_of_birth.year - ((today.month, today.day) < (home_owner.date_of_birth.month, home_owner.date_of_birth.day))

                home_owner.save()
                request.session['verified_email'] = email  # Ensure email stays in session
                messages.success(request, 'Account created successfully!')
                return redirect('HomeOwnerdashboard')
            except Exception as e:
                messages.error(request, f'Error saving data: {str(e)}')
                logger.error(f"Error saving homeowner: {str(e)}")
        else:
            messages.error(request, 'Please correct the form errors')
            logger.error(f"Form errors: {form.errors}")

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
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'role': role, 'is_active': True}
        )

        if not created and user.role != role:
            user.role = role
            user.save()

        user.otp = generate_otp()
        user.otp_created_at = timezone.now()
        user.save()

        # Send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your verification code is: {user.otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'OTP sent successfully'})
    except Exception as e:
        logger.error(f"OTP send error: {str(e)}")
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
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

        # Verify OTP
        if not user.otp or user.otp != otp:
            return JsonResponse({'success': False, 'error': 'Invalid OTP'}, status=400)

        # Check OTP expiration (5 minutes)
        if not user.otp_created_at or (timezone.now() - user.otp_created_at).total_seconds() > 300:
            return JsonResponse({'success': False, 'error': 'OTP has expired'}, status=400)

        # Clear OTP
        user.otp = None
        user.save()

        # Store the verified email in the session
        request.session['verified_email'] = email

        # Redirect based on role
        redirect_url = reverse('index') + f'?role={role}'
        if role == 'tenant':
            redirect_url = reverse('Registration')
        elif role == 'home_owner':
            redirect_url = reverse('signup_homeowner') #Corrected typo here
        elif role == 'police':
            redirect_url = reverse('Policedashboard')

        return JsonResponse({
            'success': True, 
            'message': 'OTP verified successfully',
            'redirect_url': redirect_url
        })

    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def payment(request):
    """
    View for handling the payment page for police verification
    """
    tenant_id = request.GET.get('tenant_id')
    tenant = None

    if tenant_id:
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            messages.error(request, "Tenant not found")
            return redirect('Policedashboard')

    return render(request, 'Payment.html', {'tenant': tenant})

def process_payment(request):
    """
    Process the payment for police verification
    """
    if request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        payment_method = request.POST.get('payment_method')
        amount = request.POST.get('amount', '150.00')

        try:
            # Validate tenant if ID is provided
            tenant = None
            if tenant_id:
                tenant = get_object_or_404(Tenant, id=tenant_id)

            # In a real scenario, you would integrate with a payment gateway here
            # For demo purposes, we'll simulate a successful payment

            # Update tenant status if tenant exists
            if tenant:
                tenant.police_status = 'approved'
                tenant.save()

                # Send email notification
                try:
                    send_mail(
                        'Payment Successful - Police Verification',
                        f'Dear {tenant.first_name} {tenant.last_name},\n\nYour payment of ₹{amount} for police verification has been received successfully. Your verification process will be completed soon.',
                        settings.DEFAULT_FROM_EMAIL,
                        [tenant.user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Email error: {str(e)}")

            messages.success(request, "Payment successful! The verification process will be completed soon.")
            return JsonResponse({
                'success': True,
                'message': 'Payment processed successfully',
                'redirect_url': reverse('Policedashboard')
            })

        except Tenant.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tenant not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing the payment'
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)