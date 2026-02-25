from django.contrib import admin

from .models import CustomerAccount


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
