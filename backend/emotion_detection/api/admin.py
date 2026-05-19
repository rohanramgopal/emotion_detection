"""
Admin configuration for API app.
"""
from django.contrib import admin
from .models import (
    UserProfile, EmotionAnalysis, EmotionHistory,
    Recommendation, ProviderLog, FallbackLog, AdminLog
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme_preference', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('theme_preference', 'created_at')


@admin.register(EmotionAnalysis)
class EmotionAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'emotion', 'analysis_type', 'confidence', 'provider_used', 'created_at')
    search_fields = ('user__username', 'emotion', 'text_input', 'voice_transcript')
    list_filter = ('emotion', 'analysis_type', 'provider_used', 'created_at')
    readonly_fields = ('user', 'created_at', 'updated_at')


@admin.register(EmotionHistory)
class EmotionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'daily_emotion', 'dominant_emotion', 'analysis_count')
    search_fields = ('user__username', 'daily_emotion')
    list_filter = ('date', 'daily_emotion')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'emotion', 'created_at')
    search_fields = ('emotion', 'analysis__user__username')
    list_filter = ('emotion', 'created_at')


@admin.register(ProviderLog)
class ProviderLogAdmin(admin.ModelAdmin):
    list_display = ('provider', 'status', 'response_time_ms', 'request_time')
    search_fields = ('provider', 'status')
    list_filter = ('provider', 'status', 'request_time')
    readonly_fields = ('request_time',)


@admin.register(FallbackLog)
class FallbackLogAdmin(admin.ModelAdmin):
    list_display = ('primary_provider', 'fallback_provider', 'created_at')
    search_fields = ('primary_provider', 'fallback_provider')
    list_filter = ('created_at',)


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'action', 'timestamp')
    search_fields = ('admin_user__username', 'action')
    list_filter = ('timestamp',)
    readonly_fields = ('timestamp',)
