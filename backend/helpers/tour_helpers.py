"""
Helper functions for tour-related operations.

This module contains utility functions for parsing time and distance constraints
used in tour generation and validation.
"""


def parse_time_to_minutes(time_str: str) -> int:
    """
    Parse a time string to minutes.
    
    Supports various formats:
    - "2 hours" or "2 hour" -> 120 minutes
    - "30 min" or "30 minutes" -> 30 minutes
    - "1 day" or "1 days" -> 1440 minutes
    
    Args:
        time_str: Time string in various formats (e.g., "2 hours", "30 min", "1 day")
        
    Returns:
        Time in minutes as an integer. Defaults to 120 (2 hours) if parsing fails.
    """
    if not isinstance(time_str, str):
        # If already a number, assume it's already in minutes
        return int(time_str) if time_str else 120
    
    time_lower = time_str.lower()
    if 'hour' in time_lower:
        hours = float(''.join(filter(lambda x: x.isdigit() or x == '.', time_lower.split('hour')[0])))
        return int(hours * 60)
    elif 'min' in time_lower:
        return int(''.join(filter(str.isdigit, time_lower)))
    elif 'day' in time_lower:
        days = float(''.join(filter(lambda x: x.isdigit() or x == '.', time_lower.split('day')[0])))
        return int(days * 24 * 60)
    return 120  # Default 2 hours


def parse_distance_to_km(distance_str: str) -> float:
    """
    Parse a distance string to kilometers.
    
    Supports various formats:
    - "5 km" or "5 kilometers" -> 5.0 km
    - "3 miles" or "3 mile" -> 4.828 km (converted)
    - "1000 m" or "1000 meters" -> 1.0 km (converted)
    
    Args:
        distance_str: Distance string in various formats (e.g., "5 km", "3 miles", "1000 m")
        
    Returns:
        Distance in kilometers as a float. Defaults to 5.0 km if parsing fails.
    """
    if not isinstance(distance_str, str):
        # If already a number, assume it's already in km
        return float(distance_str) if distance_str else 5.0
    
    distance_lower = distance_str.lower()
    if 'km' in distance_lower or 'kilometer' in distance_lower:
        return float(''.join(filter(lambda x: x.isdigit() or x == '.', distance_lower.split('km')[0])))
    elif 'mile' in distance_lower:
        miles = float(''.join(filter(lambda x: x.isdigit() or x == '.', distance_lower.split('mile')[0])))
        return miles * 1.60934
    elif 'm' in distance_lower and 'km' not in distance_lower:
        meters = float(''.join(filter(str.isdigit, distance_lower)))
        return meters / 1000
    return 5.0  # Default 5 km
