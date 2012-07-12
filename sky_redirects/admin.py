
from django.contrib import admin
from sky_redirects.models import DomainRedirect


class DomainRedirectAdmin(admin.ModelAdmin):
    list_display = ('redirect_from','redirect_to', 'redirect_type')

    def redirect_from(self, obj):
        return obj.fqdn

admin.site.register(DomainRedirect, DomainRedirectAdmin)