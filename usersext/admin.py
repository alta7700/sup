from django.contrib import admin
from .models import DeansUser


class DeansUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'faculty', 'courses_n', 'user')
    list_filter = ('faculty', )
    ordering = ('faculty', 'courses_n', 'user')


admin.site.register(DeansUser, DeansUserAdmin)
