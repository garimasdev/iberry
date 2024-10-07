from django.contrib import admin

from dashboard.models import *

# Register your models here.
admin.site.register(Pbx)
admin.site.register(Room)
admin.site.register(Table)
admin.site.register(Janus)
admin.site.register(Global)
admin.site.register(Extension)
admin.site.register(Dialer)
admin.site.register(Service)
admin.site.register(Complain)
admin.site.register(TermHeading)
admin.site.register(SubHeading)

