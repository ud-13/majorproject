from django.contrib import admin
from .models import Tenant, FamilyMember, PreviousResidence

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1

class PreviousResidenceInline(admin.TabularInline):
    model = PreviousResidence
    extra = 1

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'tenant_phone_number', 'district', 'created_at')
    list_filter = ('district', 'profession', 'created_at')
    search_fields = ('first_name', 'last_name', 'tenant_phone_number', 'owner_phone_number')
    inlines = [FamilyMemberInline, PreviousResidenceInline]

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'relationship', 'tenant')
    list_filter = ('relationship',)
    search_fields = ('first_name', 'last_name', 'tenant__first_name', 'tenant__last_name')

@admin.register(PreviousResidence)
class PreviousResidenceAdmin(admin.ModelAdmin):
    list_display = ('from_place', 'to_place', 'tenant')
    search_fields = ('from_place', 'to_place', 'tenant__first_name', 'tenant__last_name')