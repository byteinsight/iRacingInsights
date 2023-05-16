from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from irstats.models import *

#####  Adds an inline field to the user profile #####
class CustIDInline(admin.StackedInline):
    model = CustID
    can_delete = False
    verbose_name_plural = 'Cust ID'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [CustIDInline]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Only enable if need to add a further category
#admin.site.register(Category)

# Update Intervals
class UpdateAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'interval', 'last_update', 'next_update']
admin.site.register(Update, UpdateAdmin)

admin.site.register(Leagues)
admin.site.register(LeaguePoints)

