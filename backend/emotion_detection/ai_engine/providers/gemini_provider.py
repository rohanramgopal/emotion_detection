"""
Gemini provider for emotion detection.
"""
from google import genai
from google.genai import types
import base64
import logging
import json
import re
from .base_provider import BaseProvider

logger = logging.getLogger('emotion_detection')

EMOTION_ANALYSIS_PROMPT = """Analyze the emotional state expressed in the following text.
Respond in JSON format ONLY with these fields:
{{
    "emotion": "one of: happy, sad, angry, fear, disgust, surprise, neutral, stressed, motivated, confused",
    "confidence": 0.0-1.0,
    "reason": "brief explanation",
    "suggestions": ["suggestion1", "suggestion2"]
}}

Text to analyze: {text}"""

IMAGE_ANALYSIS_PROMPT = """Analyze the facial expression and emotional state in this image.
Respond in JSON format ONLY with these fields:
{{
    "emotion": "one of: happy, sad, angry, fear, disgust, surprise, neutral, stressed, motivated, confused",
    "confidence": 0.0-1.0,
    "reason": "brief explanation of facial features and emotion",
    "suggestions": ["suggestion1", "suggestion2"]
}}"""


class GeminiProvider(BaseProvider):
    """Gemini provider for emotion detection using Google's Generative AI."""

    def __init__(self, api_key):
        """Initialize Gemini provider."""
        super().__init__(api_key)
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.5-flash'

    def _parse_json(self, text):
        """Extract and parse JSON from model response text."""
        text = text.strip()
        # Strip markdown code fences if present
        text = re.sub(r'^```[a-z]*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(text)

    def analyze_text(self, text):
        """
        Analyze emotion from text using Gemini.

        Args:
            text (str): Text to analyze

        Returns:
            dict: Emotion analysis result
        """
        try:
            prompt = EMOTION_ANALYSIS_PROMPT.format(text=text)
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            result = self._parse_json(response.text)
            return self.format_response(
                emotion=result.get('emotion', 'neutral'),
                confidence=float(result.get('confidence', 0.5)),
                reason=result.get('reason', 'Gemini analysis'),
                suggestions=result.get('suggestions', []),
                provider_name='gemini',
                tokens_used=None
            )
        except Exception as e:
            logger.error(f"Gemini text analysis error: {str(e)}")
            raise

    def analyze_image(self, image_file):
        """
        Analyze emotion from image using Gemini Vision.

        Args:
            image_file: Image file object

        Returns:
            dict: Emotion analysis result
        """
        try:
            image_data = image_file.read()
            content_type = getattr(image_file, 'content_type', 'image/jpeg')

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    IMAGE_ANALYSIS_PROMPT,
                    types.Part.from_bytes(data=image_data, mime_type=content_type)
                ]
            )
            result = self._parse_json(response.text)
            return self.format_response(
                emotion=result.get('emotion', 'neutral'),
                confidence=float(result.get('confidence', 0.5)),
                reason=result.get('reason', 'Gemini image analysis'),
                suggestions=result.get('suggestions', []),
                provider_name='gemini',
                tokens_used=None
            )
        except Exception as e:
            logger.error(f"Gemini image analysis error: {str(e)}")
            raise
