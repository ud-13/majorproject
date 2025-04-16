from django import forms
from .models import Tenant, HomeOwner, FamilyMember, PreviousResidence, User

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'serving_certificate': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'retired_certificate': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'sikkim_certificate_file': forms.FileInput(attrs={'accept': 'image/*, .pdf'}),
            'signature_date': forms.DateInput(attrs={'type': 'date'}),
        }

class HomeOwnerForm(forms.ModelForm):
    class Meta:
        model = HomeOwner
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = '__all__'

class PreviousResidenceForm(forms.ModelForm):
    class Meta:
        model = PreviousResidence
        fields = '__all__'

class OTPVerificationForm(forms.Form):
    email = forms.EmailField()
    otp = forms.CharField(max_length=6)