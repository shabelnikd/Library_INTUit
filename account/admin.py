from django.contrib import admin
from django.contrib.admin import ModelAdmin

from account.models import AbstractUser, Group


@admin.action(description="Make user is staff")
def set_is_staff(self, request, queryset):
    queryset.update(is_staff=True)


class UserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_type', "is_staff"]
    search_fields = ['full_name']
    list_filter = ('user_type',)
    actions = [set_is_staff]


admin.site.register(AbstractUser, UserAdmin)

admin.site.register(Group)
