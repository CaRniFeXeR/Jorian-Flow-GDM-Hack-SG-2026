import os
import json
import google.generativeai as genai
from typing import Dict, List


def get_prompt_template(address: str) -> str:
    """
    Generate the prompt template for Gemini API to create thematic tour options.

    Args:
        address: The location address for which to generate tour themes

    Returns:
        Formatted prompt string
    """
    prompt = f"""You are a creative tour guide and travel expert. Given a location address, generate 5 unique and engaging thematic tour options that visitors could experience at or near this location.

Location Address: {address}

Please analyze this location and suggest 5 different thematic tour options. Each theme should be creative, specific to the location's characteristics, and appeal to different types of travelers.

IMPORTANT: Return ONLY a valid JSON object with the following structure, nothing else:
{{
    "theme_name_1": "A one-line engaging summary of what this tour offers",
    "theme_name_2": "A one-line engaging summary of what this tour offers",
    "theme_name_3": "A one-line engaging summary of what this tour offers",
    "theme_name_4": "A one-line engaging summary of what this tour offers",
    "theme_name_5": "A one-line engaging summary of what this tour offers"
}}

Guidelines:
- Make theme names catchy and descriptive (e.g., "Historical Heritage Walk", "Foodie's Paradise Tour", "Architectural Marvels")
- Keep summaries to one engaging sentence (max 20 words)
- Consider the location's history, culture, food, architecture, nature, shopping, nightlife, and local experiences
- Make each theme distinct and appealing to different traveler interests
- Ensure the JSON is properly formatted with double quotes

Return ONLY the JSON object, no additional text or explanation."""

    return prompt


async def generate_theme_options(address: str) -> Dict[str, str]:
    """
    Generate thematic tour options using Gemini API.

    Args:
        address: The location address for generating tour themes

    Returns:
        Dictionary mapping theme names to their descriptions

    Raises:
        Exception: If API call fails or response is invalid
    """
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)

    # Initialize the model
    model = genai.GenerativeModel('gemini-3-flash-preview')

    # Get the prompt
    prompt = get_prompt_template(address)

    try:
        # Generate content
        response = model.generate_content(prompt)

        # Extract the response text
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON response
        themes = json.loads(response_text)

        return themes

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")


def get_poi_prompt_template(address: str, time_constraint: str, distance_constraint: str, user_custom_info: str) -> str:
    """
    Generate the prompt template for Gemini API to create a list of POIs (Points of Interest).

    Args:
        address: The user's current location address
        time_constraint: Time available for visiting POIs (e.g., "2 hours", "half day", "full day")
        distance_constraint: Maximum distance to travel (e.g., "1 km", "5 miles", "walking distance")
        user_custom_info: Additional user preferences or requirements

    Returns:
        Formatted prompt string
    """
    prompt = f"""You are a knowledgeable local tour guide. Based on the user's current location and their constraints, recommend relevant Points of Interest (POIs) they can visit.

User Location: {address}

Constraints:
- Time Available: {time_constraint}
- Maximum Distance: {distance_constraint}
- User Preferences: {user_custom_info}

Please generate a list of POIs that match these constraints. Consider the time needed to travel and visit each location.

IMPORTANT: Return ONLY a valid JSON array with the following structure, nothing else:
[
    {{
        "poi_title": "Name of the POI",
        "poi_address": "Full address of the POI"
    }},
    {{
        "poi_title": "Name of the POI",
        "poi_address": "Full address of the POI"
    }}
]

Guidelines:
- Generate 5-10 POIs that can realistically be visited within the given time and distance constraints
- Prioritize POIs that match the user's preferences
- Include a variety of POI types (attractions, restaurants, parks, museums, shops, etc.) unless user preferences specify otherwise
- Ensure each POI title is clear and descriptive
- Provide complete, accurate addresses for each POI
- Order POIs by relevance and proximity
- Ensure the JSON is properly formatted with double quotes
- Consider travel time between POIs when selecting them

Return ONLY the JSON array, no additional text or explanation."""

    return prompt


async def generate_pois(address: str, time_constraint: str, distance_constraint: str, user_custom_info: str) -> List[Dict[str, str]]:
    """
    Generate a list of POIs using Gemini API based on location and constraints.

    Args:
        address: The user's current location address
        time_constraint: Time available for visiting POIs
        distance_constraint: Maximum distance to travel
        user_custom_info: Additional user preferences

    Returns:
        List of dictionaries containing poi_title and poi_address

    Raises:
        Exception: If API call fails or response is invalid
    """
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)

    # Initialize the model
    model = genai.GenerativeModel('gemini-3-flash-preview')

    # Get the prompt
    prompt = get_poi_prompt_template(address, time_constraint, distance_constraint, user_custom_info)

    try:
        # Generate content
        response = model.generate_content(prompt)

        # Extract the response text
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON response
        pois = json.loads(response_text)

        # Validate that it's a list
        if not isinstance(pois, list):
            raise Exception("Expected a list of POIs from Gemini API")

        # Validate each POI has required fields
        for poi in pois:
            if not isinstance(poi, dict) or 'poi_title' not in poi or 'poi_address' not in poi:
                raise Exception("Invalid POI format in response")

        return pois

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")
