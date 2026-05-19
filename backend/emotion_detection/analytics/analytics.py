"""
Analytics module for emotion detection.
"""
from django.db.models import Count, Avg, Q
from api.models import EmotionAnalysis, ProviderLog
import logging

logger = logging.getLogger('emotion_detection')


class AnalyticsEngine:
    """Engine for generating analytics data."""
    
    @staticmethod
    def get_emotion_distribution(user=None):
        """Get emotion distribution statistics."""
        queryset = EmotionAnalysis.objects.all()
        if user:
            queryset = queryset.filter(user=user)
        
        return dict(queryset.values('emotion').annotate(count=Count('id')).values_list('emotion', 'count'))
    
    @staticmethod
    def get_provider_performance():
        """Get provider performance metrics."""
        stats = ProviderLog.objects.values('provider').annotate(
            total_requests=Count('id'),
            success_count=Count('id', filter=Q(status='success')),
            failed_count=Count('id', filter=Q(status='failed')),
            avg_response_time=Avg('response_time_ms')
        ).order_by('-total_requests')
        
        return list(stats)
    
    @staticmethod
    def get_user_trends(user):
        """Get user emotion trends."""
        analyses = EmotionAnalysis.objects.filter(user=user).order_by('-created_at')[:30]
        
        trends = {
            'total': analyses.count(),
            'avg_confidence': analyses.aggregate(Avg('confidence'))['confidence__avg'] or 0,
            'most_common': EmotionAnalysis.objects.filter(user=user).values('emotion').annotate(
                count=Count('id')
            ).order_by('-count').first(),
        }
        
        return trends
