from django.contrib import admin

# Register your models here.

from .models import (
    portal_photo_details,
    country_details,
    state_details,
    district_details,
    taluk_details,
    village_town_details,
    shop_details,
)

@admin.register(portal_photo_details)
class PortalPhotoDetailsAdmin(admin.ModelAdmin):
    list_display = ('portal_type', 'badge_text', 'display_order', 'is_active')
    list_filter = ('portal_type', 'is_active')
    ordering = ('portal_type', 'display_order')



admin.site.register(country_details)
admin.site.register(state_details)
admin.site.register(district_details)
admin.site.register(taluk_details)
admin.site.register(village_town_details)
admin.site.register(shop_details)    