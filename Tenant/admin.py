from django.contrib import admin
from .models import Tenant, FamilyMember, PreviousResidence, User, HomeOwner

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 1

class PreviousResidenceInline(admin.TabularInline):
    model = PreviousResidence
    extra = 1

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'tenant_phone_number', 'district', 'status', 'police_status', 'created_at')
    list_filter = ('district', 'profession', 'status', 'police_status', 'created_at')
    search_fields = ('first_name', 'last_name', 'tenant_phone_number', 'owner_phone_number')
    inlines = [FamilyMemberInline, PreviousResidenceInline]
    actions = ['approve_tenants', 'reject_tenants']
    
    def approve_tenants(self, request, queryset):
        queryset.update(status='approved')
    approve_tenants.short_description = "Mark selected tenants as approved"
    
    def reject_tenants(self, request, queryset):
        queryset.update(status='rejected')
    reject_tenants.short_description = "Mark selected tenants as rejected"

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'relationship', 'tenant')
    list_filter = ('relationship',)
    search_fields = ('first_name', 'last_name', 'tenant__first_name', 'tenant__last_name')

@admin.register(PreviousResidence)
class PreviousResidenceAdmin(admin.ModelAdmin):
    list_display = ('from_place', 'to_place', 'tenant')
    search_fields = ('from_place', 'to_place', 'tenant__first_name', 'tenant__last_name')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('date_joined', 'otp', 'otp_created_at')}),
    )
    ordering = ('-date_joined',)

@admin.register(HomeOwner)
class HomeOwnerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'aadhar_number')
    list_filter = ('created_at',)
