"""
Utility functions for emotion detection.
"""
import logging

logger = logging.getLogger('emotion_detection')


def normalize_emotion(emotion_str):
    """Normalize emotion string to standard format."""
    emotion_lower = emotion_str.lower().strip()
    valid_emotions = [
        'happy', 'sad', 'angry', 'fear', 'disgust',
        'surprise', 'neutral', 'stressed', 'motivated', 'confused'
    ]
    
    if emotion_lower in valid_emotions:
        return emotion_lower
    
    # Try to find closest match
    for valid_emotion in valid_emotions:
        if valid_emotion in emotion_lower or emotion_lower in valid_emotion:
            return valid_emotion
    
    return 'neutral'  # Default


def normalize_confidence(confidence):
    """Normalize confidence to 0-1 range."""
    try:
        conf = float(confidence)
        return min(max(conf, 0), 1)
    except (ValueError, TypeError):
        return 0.5


def parse_emotion_response(response_text):
    """Parse emotion response from AI provider."""
    import json
    import re
    
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return json.loads(response_text)
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Failed to parse emotion response: {str(e)}")
        return None
