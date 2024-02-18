from django.contrib import admin

from dashboard.models import Complain, Dialer, Extension, Global, Janus, Pbx, Room, Service

# Register your models here.
admin.site.register(Pbx)
admin.site.register(Room)
admin.site.register(Janus)
admin.site.register(Global)
admin.site.register(Extension)
admin.site.register(Dialer)
admin.site.register(Service)
admin.site.register(Complain)
