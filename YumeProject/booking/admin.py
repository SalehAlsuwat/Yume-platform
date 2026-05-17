from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'capsule_info', 'status', 'total_price', 'check_in', 'check_out', 'quantity', 'booking_type')
    list_filter = ('status', 'booking_type', 'created_at', 'check_in')
    search_fields = ('customer__user__username', 'customer__user__email', 'capsule__hotel__name')
    readonly_fields = ('created_at', 'id')
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('id', 'customer', 'capsule', 'status', 'booking_type', 'quantity')
        }),
        ('Dates', {
            'fields': ('check_in', 'check_out')
        }),
        ('Payment', {
            'fields': ('total_price', 'commission_amount', 'commission_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'check_in'
    
    def customer_name(self, obj):
        return obj.customer.user.get_full_name() or obj.customer.user.username
    customer_name.short_description = 'Customer'
    
    def capsule_info(self, obj):
        return f'{obj.capsule.hotel.name} - Capsule {obj.capsule.capsule_num}'
    capsule_info.short_description = 'Capsule'
