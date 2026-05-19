"""
Quote recommendation engine based on detected emotions.
"""
import logging
from django.conf import settings

logger = logging.getLogger('emotion_detection')

# Static quotes for different emotions
EMOTION_QUOTES = {
    'happy': [
        "Happiness is when what you think, what you say, and what you do are in harmony. - Mahatma Gandhi",
        "The purpose of our lives is to be happy. - Dalai Lama",
        "Happiness is not by chance, but by choice. - Jim Rohn",
        "Your happiness is your responsibility.",
        "Smile more, worry less.",
    ],
    'sad': [
        "The only way out is through. - Robert Frost",
        "It's okay to not be okay. Reach out.",
        "This too shall pass.",
        "You are not alone in your struggle.",
        "Every setback is a setup for a comeback.",
    ],
    'angry': [
        "Anger is an acid that can do more harm to the vessel in which it is stored than to anything on which it is poured. - Mark Twain",
        "For every minute you are angry you lose sixty seconds of happiness. - Ralph Waldo Emerson",
        "Take a deep breath. You've got this.",
        "Pause. Breathe. Respond with wisdom.",
        "Let go of what you cannot control.",
    ],
    'fear': [
        "Courage is not the absence of fear, but action despite it. - Franklin D. Roosevelt",
        "Feel the fear and do it anyway. - Susan Jeffers",
        "You are braver than you believe, stronger than you seem.",
        "Fear is temporary. Pride is forever.",
        "Trust yourself. You know more than you think.",
    ],
    'disgust': [
        "Don't let the negative thoughts win. Focus on the positive.",
        "You deserve better, and you can achieve it.",
        "Clean slate, fresh start, new possibilities.",
        "Your worth is not determined by others' opinions.",
        "Embrace change and growth.",
    ],
    'surprise': [
        "Life is full of surprises. Enjoy the journey.",
        "The best things in life are unexpected.",
        "Embrace the unknown with curiosity.",
        "Wonder is the beginning of wisdom.",
        "Every surprise is a new opportunity.",
    ],
    'neutral': [
        "Balance is key to a fulfilled life.",
        "One day at a time.",
        "Progress over perfection.",
        "Focus on what you can control.",
        "Be present in this moment.",
    ],
    'stressed': [
        "You don't have to see the whole staircase, just take the first step. - Martin Luther King Jr.",
        "Slow down. You're enough, right now.",
        "This is temporary. You will overcome.",
        "Breathe in peace, breathe out stress.",
        "One thing at a time. You've got this.",
    ],
    'motivated': [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Great things never came from comfort zones.",
        "Keep pushing. Success is near.",
        "You are capable of amazing things.",
        "Your future self will thank you.",
    ],
    'confused': [
        "Confusion is the first step toward clarity.",
        "It's okay to not have all the answers.",
        "Take your time to think things through.",
        "Clarity comes with patience.",
        "Ask for help. That's a sign of strength.",
    ]
}


class QuoteRecommendationEngine:
    """Engine for recommending motivational quotes based on emotions."""
    
    def __init__(self):
        """Initialize quote recommendation engine."""
        self.quotes = EMOTION_QUOTES
        self.use_generative_quotes = getattr(settings, 'USE_GENERATIVE_QUOTES', False)
    
    def get_quotes(self, emotion, limit=3):
        """
        Get motivational quotes for an emotion.
        
        Args:
            emotion (str): Emotion name
            limit (int): Number of quotes to return
            
        Returns:
            list: List of quotes
        """
        emotion_lower = emotion.lower()
        
        if emotion_lower in self.quotes:
            quotes = self.quotes[emotion_lower][:limit]
        else:
            logger.warning(f"No quotes found for emotion: {emotion}")
            quotes = self.quotes['neutral'][:limit]
        
        return quotes
    
    def generate_custom_quote(self, emotion, ai_provider=None):
        """
        Generate a custom quote using AI.
        
        Args:
            emotion (str): Emotion name
            ai_provider: AI provider to use (optional)
            
        Returns:
            str: Generated quote
        """
        if not ai_provider or not self.use_generative_quotes:
            return self.get_quotes(emotion, limit=1)[0]
        
        try:
            prompt = f"""Generate one unique, inspirational quote for someone feeling {emotion}. 
                        Make it personal and helpful. Quote only, no author attribution needed."""
            
            result = ai_provider.analyze_text(prompt)
            return result.get('reason', self.get_quotes(emotion, limit=1)[0])
        
        except Exception as e:
            logger.error(f"Error generating custom quote: {str(e)}")
            return self.get_quotes(emotion, limit=1)[0]
    
    def add_custom_quote(self, emotion, quote):
        """
        Add a custom quote for an emotion.
        
        Args:
            emotion (str): Emotion name
            quote (str): Quote text
        """
        if emotion not in self.quotes:
            self.quotes[emotion] = []
        
        if quote not in self.quotes[emotion]:
            self.quotes[emotion].append(quote)
    
    def get_all_emotions_quotes(self):
        """Get all quotes for all emotions."""
        return self.quotes
