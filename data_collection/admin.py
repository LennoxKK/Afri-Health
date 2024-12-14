from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .api.models import Question, Option, Category, Response
from django.db.models import Count

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "first_name", "last_name", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "selected_option", "town", "created_at")
    list_filter = ("created_at", "location")
    search_fields = ("user__email", "question__text", "selected_option__text", "location")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    # Custom method to extract and display the town
    def town(self, obj):
        # Assuming location is a string in the format "Town, Country" (you can adjust this logic as needed)
        return obj.location.split(',')[-3:] if obj.location else None

    town.short_description = "Town"



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("text", "category__name")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("text", "question")
    list_filter = ("question__category",)
    search_fields = ("text", "question__text")
    ordering = ("text",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name", "description")
    ordering = ("name",)
    list_filter = ("created_at",)
    date_hierarchy = "created_at"

# Register the custom UserAdmin
admin.site.register(User, CustomUserAdmin)
