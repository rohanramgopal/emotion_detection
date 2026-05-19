"""
Serializers for emotion detection app.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, EmotionAnalysis, EmotionHistory, 
    Recommendation, ProviderLog, FallbackLog, AdminLog
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'avatar', 'bio', 'theme_preference', 'notification_preferences', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for Recommendation model."""
    class Meta:
        model = Recommendation
        fields = ('id', 'emotion', 'spotify_playlists', 'youtube_playlists', 'quotes', 'activities', 'resources', 'created_at')
        read_only_fields = ('id', 'created_at')


class EmotionAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for EmotionAnalysis model."""
    recommendation = RecommendationSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = EmotionAnalysis
        fields = (
            'id', 'user', 'analysis_type', 'emotion', 'confidence', 'reasoning',
            'provider_used', 'text_input', 'voice_transcript', 'image_path',
            'suggestions', 'recommendations', 'recommendation', 'created_at', 'updated_at', 'duration_ms'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'duration_ms', 'provider_used', 'emotion', 'confidence', 'reasoning', 'suggestions', 'recommendations')


class TextAnalysisSerializer(serializers.Serializer):
    """Serializer for text emotion analysis input."""
    text = serializers.CharField(max_length=5000, min_length=1)

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Text cannot be empty or just whitespace.")
        return value.strip()


class VoiceAnalysisSerializer(serializers.Serializer):
    """Serializer for voice emotion analysis input."""
    transcript = serializers.CharField(max_length=5000)
    audio_file = serializers.FileField(required=False)

    def validate_transcript(self, value):
        if not value.strip():
            raise serializers.ValidationError("Transcript cannot be empty.")
        return value.strip()


class ImageAnalysisSerializer(serializers.Serializer):
    """Serializer for image emotion analysis input."""
    image = serializers.ImageField()


class LiveAnalysisSerializer(serializers.Serializer):
    """Serializer for live camera emotion analysis."""
    frame_data = serializers.CharField()  # Base64 encoded image
    frame_count = serializers.IntegerField(min_value=1)


class MultimodalAnalysisSerializer(serializers.Serializer):
    """Serializer for multimodal emotion analysis."""
    text = serializers.CharField(max_length=5000, required=False)
    transcript = serializers.CharField(max_length=5000, required=False)
    image = serializers.ImageField(required=False)
    frame_data = serializers.CharField(required=False)

    def validate(self, data):
        if not any([data.get('text'), data.get('transcript'), data.get('image'), data.get('frame_data')]):
            raise serializers.ValidationError("At least one input type is required.")
        return data


class EmotionHistorySerializer(serializers.ModelSerializer):
    """Serializer for EmotionHistory model."""
    class Meta:
        model = EmotionHistory
        fields = ('id', 'user', 'daily_emotion', 'analysis_count', 'average_confidence', 'dominant_emotion', 'date', 'additional_data')
        read_only_fields = ('id', 'user', 'date')


class ProviderLogSerializer(serializers.ModelSerializer):
    """Serializer for ProviderLog model."""
    class Meta:
        model = ProviderLog
        fields = ('id', 'provider', 'request_time', 'response_time_ms', 'status', 'error_message', 'tokens_used', 'cost')
        read_only_fields = ('id', 'request_time')


class AdminLogSerializer(serializers.ModelSerializer):
    """Serializer for AdminLog model."""
    admin_user = UserSerializer(read_only=True)

    class Meta:
        model = AdminLog
        fields = ('id', 'admin_user', 'action', 'description', 'ip_address', 'timestamp')
        read_only_fields = ('id', 'timestamp')
