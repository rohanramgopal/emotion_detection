"""
Provider manager with fallback logic.
"""
import logging
from django.conf import settings
from .providers.gemini_provider import GeminiProvider
from .providers.groq_provider import GroqProvider
from .providers.openrouter_provider import OpenRouterProvider
from emotion_detection.api.models import FallbackLog

logger = logging.getLogger('emotion_detection')


class ProviderManager:
    """
    Manager for handling AI providers with fallback logic.
    
    Provider priority order:
    1. Gemini
    2. Groq
    3. OpenRouter
    """
    
    def __init__(self):
        """Initialize all providers."""
        self.providers = []
        
        # Initialize providers in priority order
        if settings.GEMINI_API_KEY:
            self.providers.append({
                'name': 'gemini',
                'provider': GeminiProvider(settings.GEMINI_API_KEY)
            })
        
        if settings.GROQ_API_KEY:
            self.providers.append({
                'name': 'groq',
                'provider': GroqProvider(settings.GROQ_API_KEY)
            })
        
        if settings.OPENROUTER_API_KEY:
            self.providers.append({
                'name': 'openrouter',
                'provider': OpenRouterProvider(settings.OPENROUTER_API_KEY)
            })
        
        if not self.providers:
            logger.warning("No AI providers configured!")
    
    def analyze_text(self, text, analysis_model=None):
        """
        Analyze text emotion with fallback logic.
        
        Args:
            text (str): Text to analyze
            analysis_model: Optional EmotionAnalysis model to log fallbacks
            
        Returns:
            dict: Emotion analysis result
        """
        for i, provider_info in enumerate(self.providers):
            try:
                logger.info(f"Attempting text analysis with {provider_info['name']}")
                result = provider_info['provider'].analyze_text(text)
                logger.info(f"Text analysis successful with {provider_info['name']}")
                return result
            
            except Exception as e:
                logger.error(f"Text analysis failed with {provider_info['name']}: {str(e)}")
                
                # Log fallback if this is not the last provider
                if i < len(self.providers) - 1 and analysis_model:
                    next_provider = self.providers[i + 1]['name']
                    FallbackLog.objects.create(
                        analysis=analysis_model,
                        primary_provider=provider_info['name'],
                        fallback_provider=next_provider,
                        reason=str(e)
                    )
                
                # Try next provider
                if i < len(self.providers) - 1:
                    continue
                else:
                    # All providers failed
                    raise ValueError("All emotion detection providers failed")
    
    def analyze_image(self, image_file, analysis_model=None):
        """
        Analyze image emotion with fallback logic.
        
        Args:
            image_file: Image file to analyze
            analysis_model: Optional EmotionAnalysis model to log fallbacks
            
        Returns:
            dict: Emotion analysis result
        """
        for i, provider_info in enumerate(self.providers):
            try:
                # Check if provider supports image analysis
                provider = provider_info['provider']
                if hasattr(provider, 'analyze_image'):
                    logger.info(f"Attempting image analysis with {provider_info['name']}")
                    
                    # Reset file pointer if it's seekable
                    if hasattr(image_file, 'seek'):
                        image_file.seek(0)
                    
                    result = provider.analyze_image(image_file)
                    logger.info(f"Image analysis successful with {provider_info['name']}")
                    return result
                else:
                    logger.info(f"{provider_info['name']} does not support image analysis")
                    continue
            
            except NotImplementedError:
                logger.info(f"{provider_info['name']} does not support image analysis")
                continue
            
            except Exception as e:
                logger.error(f"Image analysis failed with {provider_info['name']}: {str(e)}")
                
                # Log fallback
                if i < len(self.providers) - 1 and analysis_model:
                    next_provider = self.providers[i + 1]['name']
                    FallbackLog.objects.create(
                        analysis=analysis_model,
                        primary_provider=provider_info['name'],
                        fallback_provider=next_provider,
                        reason=str(e)
                    )
                
                continue
        
        raise ValueError("All image analysis providers failed")
    
    def analyze_multimodal(self, data, analysis_model=None):
        """
        Analyze multimodal data with fallback logic.
        
        Args:
            data (dict): Multi-input data (text, transcript, image, frame_data)
            analysis_model: Optional EmotionAnalysis model to log fallbacks
            
        Returns:
            dict: Emotion analysis result
        """
        for i, provider_info in enumerate(self.providers):
            try:
                logger.info(f"Attempting multimodal analysis with {provider_info['name']}")
                result = provider_info['provider'].analyze_multimodal(data)
                logger.info(f"Multimodal analysis successful with {provider_info['name']}")
                return result
            
            except Exception as e:
                logger.error(f"Multimodal analysis failed with {provider_info['name']}: {str(e)}")
                
                # Log fallback
                if i < len(self.providers) - 1 and analysis_model:
                    next_provider = self.providers[i + 1]['name']
                    FallbackLog.objects.create(
                        analysis=analysis_model,
                        primary_provider=provider_info['name'],
                        fallback_provider=next_provider,
                        reason=str(e)
                    )
                
                if i < len(self.providers) - 1:
                    continue
                else:
                    raise ValueError("All multimodal analysis providers failed")
    
    def get_available_providers(self):
        """Get list of available providers."""
        return [p['name'] for p in self.providers]
    
    def get_provider_status(self):
        """Get status of all providers."""
        return {
            'available_providers': self.get_available_providers(),
            'total_providers': len(self.providers),
            'status': 'operational' if self.providers else 'no_providers'
        }
