"""
Input validation utilities
"""

def validate_user_id(user_id: int) -> bool:
    """Validate user ID format"""
    return isinstance(user_id, int) and user_id > 0

def validate_song_id(song_id: int) -> bool:
    """Validate song ID format"""
    return isinstance(song_id, int) and song_id > 0

def validate_rating(rating: float) -> bool:
    """Validate rating value"""
    return isinstance(rating, (int, float)) and 1 <= rating <= 5

def validate_num_recommendations(num: int) -> bool:
    """Validate number of recommendations"""
    return isinstance(num, int) and 1 <= num <= 1000
