"""
Base provider class for emotion detection.
"""
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for all emotion detection providers."""
    
    def __init__(self, api_key):
        """Initialize provider with API key."""
        self.api_key = api_key
    
    @abstractmethod
    def analyze_text(self, text):
        """
        Analyze emotion from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: {
                'emotion': str,
                'confidence': float,
                'reason': str,
                'suggestions': list,
                'provider': str,
                'tokens_used': int (optional)
            }
        """
        pass
    
    @abstractmethod
    def analyze_image(self, image_file):
        """
        Analyze emotion from image.
        
        Args:
            image_file: Image file object
            
        Returns:
            dict: Emotion analysis result
        """
        pass
    
    def analyze_multimodal(self, data):
        """
        Analyze emotion from multiple inputs.
        
        Args:
            data (dict): Multi-input data
            
        Returns:
            dict: Emotion analysis result
        """
        # Default implementation: combine text and transcripts
        combined_text = ""
        if data.get('text'):
            combined_text += data['text'] + " "
        if data.get('transcript'):
            combined_text += data['transcript']
        
        if combined_text.strip():
            return self.analyze_text(combined_text)
        
        raise ValueError("No text or transcript provided for multimodal analysis")

    @staticmethod
    def format_response(emotion, confidence, reason, suggestions=None, provider_name="", tokens_used=None):
        """
        Format provider response to standard format.
        
        Args:
            emotion (str): Detected emotion
            confidence (float): Confidence score (0-1)
            reason (str): Explanation
            suggestions (list): Suggestions (optional)
            provider_name (str): Provider name
            tokens_used (int): Tokens used (optional)
            
        Returns:
            dict: Formatted response
        """
        response = {
            'emotion': emotion,
            'confidence': min(max(confidence, 0), 1),  # Ensure 0-1 range
            'reason': reason,
            'suggestions': suggestions or [],
            'provider': provider_name,
        }
        if tokens_used:
            response['tokens_used'] = tokens_used
        return response
