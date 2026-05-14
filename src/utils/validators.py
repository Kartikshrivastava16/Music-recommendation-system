"""
Input validation utilities
"""

from typing import Any

def validate_user_id(user_id: Any) -> bool:
    """
    Validate user ID format
    
    Args:
        user_id: Value to validate
    
    Returns:
        True if valid user ID, False otherwise
    """
    try:
        uid = int(user_id)
        return uid > 0
    except (ValueError, TypeError):
        return False

def validate_song_id(song_id: Any) -> bool:
    """
    Validate song ID format
    
    Args:
        song_id: Value to validate
    
    Returns:
        True if valid song ID, False otherwise
    """
    try:
        sid = int(song_id)
        return sid > 0
    except (ValueError, TypeError):
        return False

def validate_rating(rating: Any) -> bool:
    """
    Validate rating value
    
    Args:
        rating: Value to validate
    
    Returns:
        True if valid rating (1-5), False otherwise
    """
    try:
        r = float(rating)
        return 1 <= r <= 5
    except (ValueError, TypeError):
        return False

def validate_num_recommendations(num: int) -> bool:
    """Validate number of recommendations"""
    return isinstance(num, int) and 1 <= num <= 1000

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email to validate
    
    Returns:
        True if valid email format, False otherwise
    """
    if not isinstance(email, str):
        return False
    
    return '@' in email and '.' in email.split('@')[-1]

def validate_number(value: Any, min_val: float = None, max_val: float = None) -> bool:
    """
    Validate numeric value
    
    Args:
        value: Value to validate
        min_val: Minimum value (optional)
        max_val: Maximum value (optional)
    
    Returns:
        True if valid, False otherwise
    """
    try:
        num = float(value)
        
        if min_val is not None and num < min_val:
            return False
        
        if max_val is not None and num > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False
