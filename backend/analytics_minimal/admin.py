from django.contrib import admin

from analytics_minimal.models import (
    APIKey,
    PageView,
    Site,
)


@admin.register(APIKey)
class APIAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'site', 'active', 'created_at', 'updated_at',)
    readonly_fields = ('created_at', 'updated_at', 'token',)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'event_name', 'hostname', 'path', 'site',
                    'api_key', 'created_at', 'updated_at',)
    readonly_fields = ('created_at', 'updated_at', 'token',)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at', 'token',)

    actions = ['generate_api_keys']

    def generate_api_key(self, request, site):
        APIKey.objects.filter(site=site, active=True).update(active=False)
        APIKey.objects.create(
            site=site,
            active=True,
        )

    def generate_api_keys(self, request, queryset):
        # Prevent previous APIKeys from being used
        for site in queryset:
            self.generate_api_key(request, site)

    generate_api_keys.short_description = ('Generate new api key')
