import os
import googlemaps
from typing import Optional, Dict


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
        result = gmaps.reverse_geocode((latitude, longitude))  # type: ignore[attr-defined]

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
        result = gmaps.reverse_geocode((latitude, longitude))  # type: ignore[attr-defined]

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


def verify_poi_exists(poi_title: str, poi_address: str) -> bool:
    """
    Verify if a POI exists in reality by geocoding its address.

    Args:
        poi_title: The name/title of the POI
        poi_address: The address of the POI

    Returns:
        True if the POI address exists and is verified, False otherwise

    Raises:
        ValueError: If API key is not found
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

    try:
        gmaps = googlemaps.Client(key=api_key)

        # Geocode the address to verify it exists
        geocode_result = gmaps.geocode(poi_address)  # type: ignore[attr-defined]

        if not geocode_result or len(geocode_result) == 0:
            print(f"❌ Address not found: {poi_address}")
            return False

        result = geocode_result[0]

        # Check if this is a partial match (Google couldn't find exact address)
        if result.get('partial_match', False):
            print(f"❌ Partial match only (address doesn't fully exist): {poi_address}")
            print(f"   Google returned: {result.get('formatted_address')}")
            return False

        # Check the location type - it should be specific (street address, premise, etc.)
        # If it's just a city or country, the address is too vague/doesn't exist
        geometry = result.get('geometry', {})
        location_type = geometry.get('location_type', '')

        # ROOFTOP is exact, RANGE_INTERPOLATED is very close
        # GEOMETRIC_CENTER and APPROXIMATE are too vague
        if location_type not in ['ROOFTOP', 'RANGE_INTERPOLATED']:
            print(f"❌ Location too vague (type: {location_type}): {poi_address}")
            print(f"   Google returned: {result.get('formatted_address')}")
            return False

        # Check address types - should include street_address or premise
        types = result.get('types', [])
        valid_types = ['street_address', 'premise', 'establishment', 'point_of_interest']

        if not any(valid_type in types for valid_type in valid_types):
            print(f"❌ Address is not specific enough (types: {types}): {poi_address}")
            print(f"   Google returned: {result.get('formatted_address')}")
            return False

        formatted_address = result.get('formatted_address', '')
        print(f"✅ Verified address: {poi_address}")
        print(f"   Maps address: {formatted_address}")
        return True

    except googlemaps.exceptions.ApiError as e:
        print(f"❌ Google Maps API error while verifying POI '{poi_title}': {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error verifying POI '{poi_title}': {str(e)}")
        return False


def verify_multiple_pois(pois: list) -> list:
    """
    Verify multiple POIs and return only those that exist.

    Args:
        pois: List of POI dictionaries with 'poi_title' and 'poi_address' keys

    Returns:
        Filtered list of verified POIs

    Raises:
        ValueError: If API key is not found
    """
    verified_pois = []

    for poi in pois:
        poi_title = poi.get('poi_title', '')
        poi_address = poi.get('poi_address', '')

        if not poi_title or not poi_address:
            # Skip POIs with missing data
            continue

        # Verify if the POI exists
        if verify_poi_exists(poi_title, poi_address):
            verified_pois.append(poi)

    return verified_pois

def get_place_details(poi_title: str, poi_address: str) -> Optional[Dict]:
    """
    Get Google Place ID and name for a POI.

    Args:
        poi_title: The name/title of the POI
        poi_address: The address of the POI

    Returns:
        Dictionary with place_id and name, or None if not found

    Raises:
        ValueError: If API key is not found
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

    try:
        gmaps = googlemaps.Client(key=api_key)

        # Search for the POI using find_place
        search_query = f"{poi_title}, {poi_address}"

        result = gmaps.find_place(
            input=search_query,
            input_type="textquery",
            fields=["place_id", "name", "formatted_address"]
        )

        # Check if we got results
        if not result or 'candidates' not in result or len(result['candidates']) == 0:
            print(f"❌ No place details found for: {search_query}")
            return None

        # Get the first candidate
        candidate = result['candidates'][0]

        place_details = {
            'google_place_id': candidate.get('place_id', ''),
            'google_maps_name': candidate.get('name', poi_title),
            'formatted_address': candidate.get('formatted_address', poi_address)
        }

        print(f"✅ Found place details for '{poi_title}': {place_details['google_maps_name']} ({place_details['google_place_id']})")

        return place_details

    except googlemaps.exceptions.ApiError as e:
        print(f"❌ Google Maps API error while getting place details: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error getting place details: {str(e)}")
        return None
