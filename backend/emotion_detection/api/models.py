"""
Models for emotion detection app.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

EMOTION_CHOICES = [
    ('happy', 'Happy'),
    ('sad', 'Sad'),
    ('angry', 'Angry'),
    ('fear', 'Fear'),
    ('disgust', 'Disgust'),
    ('surprise', 'Surprise'),
    ('neutral', 'Neutral'),
    ('stressed', 'Stressed'),
    ('motivated', 'Motivated'),
    ('confused', 'Confused'),
]

PROVIDER_CHOICES = [
    ('gemini', 'Gemini'),
    ('groq', 'Groq'),
    ('openrouter', 'OpenRouter'),
]

ANALYSIS_TYPE_CHOICES = [
    ('text', 'Text Analysis'),
    ('voice', 'Voice Analysis'),
    ('image', 'Image Analysis'),
    ('live', 'Live Analysis'),
    ('multimodal', 'Multimodal Analysis'),
]


class UserProfile(models.Model):
    """Extended user profile model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    theme_preference = models.CharField(max_length=10, default='light', choices=[('light', 'Light'), ('dark', 'Dark')])
    notification_preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"


class EmotionAnalysis(models.Model):
    """Model to store emotion analysis results."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES)
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    reasoning = models.TextField()
    provider_used = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    
    # Input data
    text_input = models.TextField(null=True, blank=True)
    voice_transcript = models.TextField(null=True, blank=True)
    image_path = models.ImageField(upload_to='analyses/', null=True, blank=True)
    
    # Additional data
    raw_response = models.JSONField(default=dict)
    suggestions = models.JSONField(default=list)
    recommendations = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration_ms = models.IntegerField(null=True, blank=True)  # Processing time
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['emotion']),
            models.Index(fields=['provider_used']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.emotion} ({self.created_at})"


class EmotionHistory(models.Model):
    """Model to track emotion trends over time."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotion_history')
    daily_emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    analysis_count = models.IntegerField(default=0)
    average_confidence = models.FloatField(default=0.0)
    dominant_emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    date = models.DateField(auto_now_add=True)
    additional_data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Recommendation(models.Model):
    """Model for storing emotion-based recommendations."""
    analysis = models.OneToOneField(EmotionAnalysis, on_delete=models.CASCADE, related_name='recommendation')
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    
    # Music recommendations
    spotify_playlists = models.JSONField(default=list)  # List of Spotify URLs
    youtube_playlists = models.JSONField(default=list)  # List of YouTube URLs
    
    # Quote recommendations
    quotes = models.JSONField(default=list)
    
    # Additional recommendations
    activities = models.JSONField(default=list)
    resources = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Recommendations for {self.analysis}"


class ProviderLog(models.Model):
    """Model for logging API provider performance."""
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    analysis = models.ForeignKey(EmotionAnalysis, on_delete=models.SET_NULL, null=True, related_name='provider_logs')
    request_time = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('error', 'Error'),
    ])
    error_message = models.TextField(blank=True)
    tokens_used = models.IntegerField(null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-request_time']
        indexes = [
            models.Index(fields=['provider', '-request_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.provider} - {self.status} ({self.request_time})"


class FallbackLog(models.Model):
    """Model for tracking fallback events between providers."""
    analysis = models.ForeignKey(EmotionAnalysis, on_delete=models.CASCADE, related_name='fallback_logs')
    primary_provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    fallback_provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.primary_provider} -> {self.fallback_provider}"


class AdminLog(models.Model):
    """Model for admin activity logging."""
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_logs')
    action = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.admin_user} - {self.action} ({self.timestamp})"
