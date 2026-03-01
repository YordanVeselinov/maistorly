from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomerAccount, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id',)


@admin.register(CustomerAccount)
class CustomerAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'phone',
        'city',
        'state',
        'country',
        'created_at',
    )
    search_fields = ('user__username', 'user__email', 'phone', 'city', 'state', 'country')
    list_filter = ('country', 'state', 'city')
