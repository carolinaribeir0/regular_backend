# admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company, UserProfile, RenewableDoc, Budget, Finance, ConstitutiveDocument


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 1  # para mostrar o formulário vazio por padrão


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(RenewableDoc)
admin.site.register(Budget)
admin.site.register(Finance)
admin.site.register(ConstitutiveDocument)
