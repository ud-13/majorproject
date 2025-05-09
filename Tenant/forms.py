from django import forms
from .models import Tenant, HomeOwner, FamilyMember, PreviousResidence, User

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'
        exclude = ['user', 'status', 'police_status', 'police_remark', 'created_at', 'updated_at']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'serving_certificate': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'retired_certificate': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'sikkim_certificate_file': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'signature_date': forms.DateInput(attrs={'type': 'date'}),
            'signature': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class HomeOwnerForm(forms.ModelForm):
    class Meta:
        model = HomeOwner
        exclude = ['user']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'aadhar_card': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'sikkim_certificate': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'residential_certificate': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'land_parcha': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
        }

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = '__all__'
        exclude = ['tenant', 'created_at', 'updated_at']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class PreviousResidenceForm(forms.ModelForm):
    class Meta:
        model = PreviousResidence
        fields = '__all__'
        exclude = ['tenant', 'created_at', 'updated_at']

class OTPVerificationForm(forms.Form):
    email = forms.EmailField()
    otp = forms.CharField(max_length=6)