import os
import googlemaps
from typing import Optional


def get_address_from_coordinates(latitude: float, longitude: float) -> str:
    """
    Convert latitude and longitude coordinates to a human-readable address using Google Maps Geocoding API.

    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate

    Returns:
        Formatted address string

    Raises:
        ValueError: If API key is not found or coordinates are invalid
        Exception: If geocoding fails
    """
    # Get Google Maps API key
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

    try:
        # Initialize Google Maps client
        gmaps = googlemaps.Client(key=api_key)

        # Perform reverse geocoding
        result = gmaps.reverse_geocode((latitude, longitude))

        if not result or len(result) == 0:
            raise Exception("No address found for the given coordinates")

        # Get the formatted address from the first result
        formatted_address = result[0].get('formatted_address', '')

        if not formatted_address:
            raise Exception("Could not extract formatted address from geocoding result")

        return formatted_address

    except googlemaps.exceptions.ApiError as e:
        raise Exception(f"Google Maps API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error during reverse geocoding: {str(e)}")


def get_detailed_location_info(latitude: float, longitude: float) -> dict:
    """
    Get detailed location information including address components.

    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate

    Returns:
        Dictionary containing detailed location information

    Raises:
        ValueError: If API key is not found
        Exception: If geocoding fails
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

    try:
        gmaps = googlemaps.Client(key=api_key)
        result = gmaps.reverse_geocode((latitude, longitude))

        if not result or len(result) == 0:
            raise Exception("No location information found for the given coordinates")

        location_data = result[0]

        # Extract relevant components
        address_components = location_data.get('address_components', [])

        # Build a structured location info
        location_info = {
            'formatted_address': location_data.get('formatted_address', ''),
            'place_id': location_data.get('place_id', ''),
            'types': location_data.get('types', []),
            'components': {}
        }

        # Parse address components
        for component in address_components:
            types = component.get('types', [])
            if 'locality' in types or 'administrative_area_level_1' in types:
                location_info['components'][types[0]] = component.get('long_name', '')

        return location_info

    except Exception as e:
        raise Exception(f"Error getting location information: {str(e)}")
