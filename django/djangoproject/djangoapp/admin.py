from django.contrib import admin
from .models import Play, Rating, Report

# Register Django models (gameplay tracking only)
# Story, Page, Choice are in Flask - not registered here


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ("user", "story_id", "ending_page_id", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "story_id")
    readonly_fields = ("created_at",)

    def has_add_permission(self, request):
        # Plays are created automatically, not manually
        return False


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "story_id", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "story_id", "comment")
    readonly_fields = ("created_at",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("user", "story_id", "reason", "resolved", "created_at")
    list_filter = ("reason", "resolved", "created_at")
    search_fields = ("user__username", "story_id", "description")
    readonly_fields = ("created_at",)

    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        queryset.update(resolved=True)
        self.message_user(request, f"{queryset.count()} reports marked as resolved.")

    mark_as_resolved.short_description = "Mark selected reports as resolved"
