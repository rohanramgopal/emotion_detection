"""
URL configuration for API app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView, UserProfileView,
    TextEmotionAnalysisView, VoiceEmotionAnalysisView, ImageEmotionAnalysisView,
    MultimodalEmotionAnalysisView, EmotionAnalysisHistoryView, EmotionHistoryView,
    RecommendationView, AdminStatsView, get_recommendations, get_quotes
)

router = DefaultRouter()
router.register(r'analyses', EmotionAnalysisHistoryView, basename='analysis')
router.register(r'history', EmotionHistoryView, basename='history')
router.register(r'recommendations', RecommendationView, basename='recommendation')
router.register(r'admin/stats', AdminStatsView, basename='admin-stats')

# ViewSets without model
text_analysis = TextEmotionAnalysisView.as_view({
    'post': 'create',
})
voice_analysis = VoiceEmotionAnalysisView.as_view({
    'post': 'create',
})
image_analysis = ImageEmotionAnalysisView.as_view({
    'post': 'create',
})
multimodal_analysis = MultimodalEmotionAnalysisView.as_view({
    'post': 'create',
})

urlpatterns = [
    # Authentication
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    
    # Emotion Analysis
    path('analyze/text/', text_analysis, name='analyze-text'),
    path('analyze/voice/', voice_analysis, name='analyze-voice'),
    path('analyze/image/', image_analysis, name='analyze-image'),
    path('analyze/multimodal/', multimodal_analysis, name='analyze-multimodal'),
    
    # Recommendations
    path('recommendations/', get_recommendations, name='get-recommendations'),
    path('quotes/', get_quotes, name='get-quotes'),
    
    # Router URLs
    path('', include(router.urls)),
]
