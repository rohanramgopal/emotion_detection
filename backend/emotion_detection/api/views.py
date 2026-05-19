"""
Views for emotion detection API.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg, Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
import logging
import time
import base64
import io
from PIL import Image

from .models import (
    UserProfile, EmotionAnalysis, EmotionHistory, 
    Recommendation, ProviderLog, FallbackLog, AdminLog
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    EmotionAnalysisSerializer, TextAnalysisSerializer, VoiceAnalysisSerializer,
    ImageAnalysisSerializer, LiveAnalysisSerializer, MultimodalAnalysisSerializer,
    EmotionHistorySerializer, ProviderLogSerializer, AdminLogSerializer, RecommendationSerializer
)

# Import AI engine modules
from emotion_detection.ai_engine.provider_manager import ProviderManager
from emotion_detection.recommendations.music_engine import MusicRecommendationEngine
from emotion_detection.recommendations.quote_engine import QuoteRecommendationEngine

logger = logging.getLogger('emotion_detection')
provider_manager = ProviderManager()
music_engine = MusicRecommendationEngine()
quote_engine = QuoteRecommendationEngine()


class UserRegistrationView(CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=request.data['username'])
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserProfileView(RetrieveUpdateAPIView):
    """View for user profile."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class TextEmotionAnalysisView(viewsets.ViewSet):
    """ViewSet for text emotion analysis."""
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        """Analyze emotion from text."""
        serializer = TextAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data['text']
        start_time = time.time()

        try:
            # Get emotion analysis from provider
            result = provider_manager.analyze_text(text)
            duration_ms = int((time.time() - start_time) * 1000)

            # Save analysis to database
            analysis = EmotionAnalysis.objects.create(
                user=request.user,
                analysis_type='text',
                emotion=result['emotion'],
                confidence=result['confidence'],
                reasoning=result['reason'],
                provider_used=result['provider'],
                text_input=text,
                raw_response=result,
                suggestions=result.get('suggestions', []),
                duration_ms=duration_ms
            )

            # Get recommendations
            music_recs = music_engine.get_recommendations(result['emotion'])
            quotes = quote_engine.get_quotes(result['emotion'])

            recommendation = Recommendation.objects.create(
                analysis=analysis,
                emotion=result['emotion'],
                spotify_playlists=music_recs.get('spotify', []),
                youtube_playlists=music_recs.get('youtube', []),
                quotes=quotes
            )

            analysis.recommendations = {
                'music': music_recs,
                'quotes': quotes
            }
            analysis.save()

            # Log provider usage
            ProviderLog.objects.create(
                provider=result['provider'],
                analysis=analysis,
                response_time_ms=duration_ms,
                status='success',
                tokens_used=result.get('tokens_used')
            )

            return Response(
                EmotionAnalysisSerializer(analysis).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            return Response(
                {'error': 'Failed to analyze emotion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VoiceEmotionAnalysisView(viewsets.ViewSet):
    """ViewSet for voice emotion analysis."""
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        """Analyze emotion from voice."""
        serializer = VoiceAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transcript = serializer.validated_data['transcript']
        start_time = time.time()

        try:
            # Get emotion analysis from provider
            result = provider_manager.analyze_text(transcript)  # Voice uses text analysis
            duration_ms = int((time.time() - start_time) * 1000)

            # Save analysis to database
            analysis = EmotionAnalysis.objects.create(
                user=request.user,
                analysis_type='voice',
                emotion=result['emotion'],
                confidence=result['confidence'],
                reasoning=result['reason'],
                provider_used=result['provider'],
                voice_transcript=transcript,
                raw_response=result,
                suggestions=result.get('suggestions', []),
                duration_ms=duration_ms
            )

            # Get recommendations
            music_recs = music_engine.get_recommendations(result['emotion'])
            quotes = quote_engine.get_quotes(result['emotion'])

            recommendation = Recommendation.objects.create(
                analysis=analysis,
                emotion=result['emotion'],
                spotify_playlists=music_recs.get('spotify', []),
                youtube_playlists=music_recs.get('youtube', []),
                quotes=quotes
            )

            analysis.recommendations = {
                'music': music_recs,
                'quotes': quotes
            }
            analysis.save()

            # Log provider usage
            ProviderLog.objects.create(
                provider=result['provider'],
                analysis=analysis,
                response_time_ms=duration_ms,
                status='success',
                tokens_used=result.get('tokens_used')
            )

            return Response(
                EmotionAnalysisSerializer(analysis).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error in voice analysis: {str(e)}")
            return Response(
                {'error': 'Failed to analyze emotion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImageEmotionAnalysisView(viewsets.ViewSet):
    """ViewSet for image emotion analysis."""
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        """Analyze emotion from image."""
        serializer = ImageAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image_file = serializer.validated_data['image']
        start_time = time.time()

        try:
            # Get emotion analysis from provider
            result = provider_manager.analyze_image(image_file)
            duration_ms = int((time.time() - start_time) * 1000)

            # Save analysis to database
            analysis = EmotionAnalysis.objects.create(
                user=request.user,
                analysis_type='image',
                emotion=result['emotion'],
                confidence=result['confidence'],
                reasoning=result['reason'],
                provider_used=result['provider'],
                image_path=image_file,
                raw_response=result,
                suggestions=result.get('suggestions', []),
                duration_ms=duration_ms
            )

            # Get recommendations
            music_recs = music_engine.get_recommendations(result['emotion'])
            quotes = quote_engine.get_quotes(result['emotion'])

            recommendation = Recommendation.objects.create(
                analysis=analysis,
                emotion=result['emotion'],
                spotify_playlists=music_recs.get('spotify', []),
                youtube_playlists=music_recs.get('youtube', []),
                quotes=quotes
            )

            analysis.recommendations = {
                'music': music_recs,
                'quotes': quotes
            }
            analysis.save()

            # Log provider usage
            ProviderLog.objects.create(
                provider=result['provider'],
                analysis=analysis,
                response_time_ms=duration_ms,
                status='success',
                tokens_used=result.get('tokens_used')
            )

            return Response(
                EmotionAnalysisSerializer(analysis).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error in image analysis: {str(e)}")
            return Response(
                {'error': 'Failed to analyze emotion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MultimodalEmotionAnalysisView(viewsets.ViewSet):
    """ViewSet for multimodal emotion analysis."""
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        """Analyze emotion from multiple inputs."""
        serializer = MultimodalAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_time = time.time()

        try:
            data = serializer.validated_data
            # Fuse multiple inputs for analysis
            result = provider_manager.analyze_multimodal(data)
            duration_ms = int((time.time() - start_time) * 1000)

            # Save analysis to database
            analysis = EmotionAnalysis.objects.create(
                user=request.user,
                analysis_type='multimodal',
                emotion=result['emotion'],
                confidence=result['confidence'],
                reasoning=result['reason'],
                provider_used=result['provider'],
                text_input=data.get('text'),
                voice_transcript=data.get('transcript'),
                raw_response=result,
                suggestions=result.get('suggestions', []),
                duration_ms=duration_ms
            )

            # Get recommendations
            music_recs = music_engine.get_recommendations(result['emotion'])
            quotes = quote_engine.get_quotes(result['emotion'])

            recommendation = Recommendation.objects.create(
                analysis=analysis,
                emotion=result['emotion'],
                spotify_playlists=music_recs.get('spotify', []),
                youtube_playlists=music_recs.get('youtube', []),
                quotes=quotes
            )

            analysis.recommendations = {
                'music': music_recs,
                'quotes': quotes
            }
            analysis.save()

            # Log provider usage
            ProviderLog.objects.create(
                provider=result['provider'],
                analysis=analysis,
                response_time_ms=duration_ms,
                status='success',
                tokens_used=result.get('tokens_used')
            )

            return Response(
                EmotionAnalysisSerializer(analysis).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Error in multimodal analysis: {str(e)}")
            return Response(
                {'error': 'Failed to analyze emotion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmotionAnalysisHistoryView(viewsets.ModelViewSet):
    """ViewSet for emotion analysis history."""
    serializer_class = EmotionAnalysisSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('analysis_type', 'emotion', 'provider_used')
    search_fields = ('text_input', 'voice_transcript', 'reasoning')
    ordering_fields = ('created_at', 'confidence')
    ordering = ('-created_at',)

    def get_queryset(self):
        return EmotionAnalysis.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get emotion analysis statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_analyses': queryset.count(),
            'emotion_distribution': dict(queryset.values('emotion').annotate(count=Count('id')).values_list('emotion', 'count')),
            'provider_distribution': dict(queryset.values('provider_used').annotate(count=Count('id')).values_list('provider_used', 'count')),
            'average_confidence': queryset.aggregate(Avg('confidence'))['confidence__avg'] or 0,
            'analysis_types': dict(queryset.values('analysis_type').annotate(count=Count('id')).values_list('analysis_type', 'count')),
        }
        return Response(stats)


class EmotionHistoryView(viewsets.ModelViewSet):
    """ViewSet for emotion history tracking."""
    serializer_class = EmotionHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return EmotionHistory.objects.filter(user=self.request.user)


class RecommendationView(viewsets.ModelViewSet):
    """ViewSet for recommendations."""
    serializer_class = RecommendationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Recommendation.objects.filter(analysis__user=self.request.user)


class AdminStatsView(viewsets.ViewSet):
    """ViewSet for admin statistics."""
    permission_classes = (permissions.IsAdminUser,)

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get admin overview statistics."""
        stats = {
            'total_users': User.objects.count(),
            'total_analyses': EmotionAnalysis.objects.count(),
            'total_providers_used': EmotionAnalysis.objects.values('provider_used').distinct().count(),
            'emotion_distribution': dict(EmotionAnalysis.objects.values('emotion').annotate(count=Count('id')).values_list('emotion', 'count')),
            'provider_distribution': dict(EmotionAnalysis.objects.values('provider_used').annotate(count=Count('id')).values_list('provider_used', 'count')),
            'analysis_types': dict(EmotionAnalysis.objects.values('analysis_type').annotate(count=Count('id')).values_list('analysis_type', 'count')),
            'provider_logs': dict(ProviderLog.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def provider_performance(self, request):
        """Get provider performance metrics."""
        provider_stats = ProviderLog.objects.values('provider').annotate(
            total_requests=Count('id'),
            success_rate=Count('id', filter=Q(status='success')) * 100.0 / Count('id'),
            avg_response_time=Avg('response_time_ms'),
            failed_requests=Count('id', filter=Q(status='failed')),
            timeout_requests=Count('id', filter=Q(status='timeout')),
        ).order_by('-total_requests')
        
        return Response(list(provider_stats))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_recommendations(request):
    """Get music and quote recommendations based on emotion."""
    emotion = request.query_params.get('emotion')
    
    if not emotion:
        return Response({'error': 'Emotion parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    music_recs = music_engine.get_recommendations(emotion)
    quotes = quote_engine.get_quotes(emotion)
    
    return Response({
        'music': music_recs,
        'quotes': quotes
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_quotes(request):
    """Get motivational quotes."""
    emotion = request.query_params.get('emotion', 'neutral')
    quotes = quote_engine.get_quotes(emotion)
    
    return Response({'quotes': quotes})
