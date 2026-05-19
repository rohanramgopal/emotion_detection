"""
Music recommendation engine based on detected emotions.
"""
import logging

logger = logging.getLogger('emotion_detection')

# Emotion-to-Playlist mapping
EMOTION_PLAYLISTS = {
    'happy': {
        'spotify': ['https://open.spotify.com/search/happy%20music/playlists', 'https://open.spotify.com/search/feel%20good/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=happy+songs+playlist', 'https://www.youtube.com/results?search_query=feel+good+music+playlist']
    },
    'sad': {
        'spotify': ['https://open.spotify.com/search/sad%20songs/playlists', 'https://open.spotify.com/search/melancholy/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=sad+music+playlist', 'https://www.youtube.com/results?search_query=emotional+songs+playlist']
    },
    'angry': {
        'spotify': ['https://open.spotify.com/search/angry%20music/playlists', 'https://open.spotify.com/search/heavy%20metal/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=workout+music+playlist', 'https://www.youtube.com/results?search_query=aggressive+music+playlist']
    },
    'fear': {
        'spotify': ['https://open.spotify.com/search/calming%20music/playlists', 'https://open.spotify.com/search/peaceful%20piano/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=relaxing+music+playlist', 'https://www.youtube.com/results?search_query=calming+anxiety+music+playlist']
    },
    'disgust': {
        'spotify': ['https://open.spotify.com/search/mood%20boost/playlists', 'https://open.spotify.com/search/positive%20vibes/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=uplifting+music+playlist', 'https://www.youtube.com/results?search_query=positive+energy+music+playlist']
    },
    'surprise': {
        'spotify': ['https://open.spotify.com/search/new%20music/playlists', 'https://open.spotify.com/search/pop%20rising/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=latest+hits+playlist', 'https://www.youtube.com/results?search_query=trending+music+playlist']
    },
    'neutral': {
        'spotify': ['https://open.spotify.com/search/focus%20music/playlists', 'https://open.spotify.com/search/lofi%20beats/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=study+music+playlist', 'https://www.youtube.com/results?search_query=lofi+hip+hop+radio']
    },
    'stressed': {
        'spotify': ['https://open.spotify.com/search/stress%20relief/playlists', 'https://open.spotify.com/search/meditation/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=stress+relief+music+playlist', 'https://www.youtube.com/results?search_query=meditation+music+playlist']
    },
    'motivated': {
        'spotify': ['https://open.spotify.com/search/motivation/playlists', 'https://open.spotify.com/search/workout/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=motivational+music+playlist', 'https://www.youtube.com/results?search_query=workout+music+playlist']
    },
    'confused': {
        'spotify': ['https://open.spotify.com/search/clarity/playlists', 'https://open.spotify.com/search/deep%20focus/playlists'],
        'youtube': ['https://www.youtube.com/results?search_query=brain+boost+music+playlist', 'https://www.youtube.com/results?search_query=focus+music+playlist']
    }
}


class MusicRecommendationEngine:
    """Engine for recommending music based on emotions."""
    
    def __init__(self):
        """Initialize music recommendation engine."""
        self.playlists = EMOTION_PLAYLISTS
    
    def get_recommendations(self, emotion):
        """
        Get music recommendations for an emotion.
        
        Args:
            emotion (str): Emotion name
            
        Returns:
            dict: Spotify and YouTube playlists
        """
        emotion_lower = emotion.lower()
        
        if emotion_lower in self.playlists:
            return self.playlists[emotion_lower]
        else:
            logger.warning(f"No playlists found for emotion: {emotion}")
            return self.playlists['neutral']  # Default to neutral
    
    def add_custom_playlist(self, emotion, platform, url):
        """
        Add a custom playlist for an emotion.
        
        Args:
            emotion (str): Emotion name
            platform (str): 'spotify' or 'youtube'
            url (str): Playlist URL
        """
        if emotion not in self.playlists:
            self.playlists[emotion] = {'spotify': [], 'youtube': []}
        
        if platform in self.playlists[emotion]:
            if url not in self.playlists[emotion][platform]:
                self.playlists[emotion][platform].append(url)
