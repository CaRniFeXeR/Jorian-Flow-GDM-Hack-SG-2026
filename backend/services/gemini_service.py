import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional


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
- Each theme name MUST start with a relevant emoji that represents the theme (e.g., "🏛️ Historical Heritage Walk", "🍜 Foodie's Paradise Tour", "🏗️ Architectural Marvels")
- Make theme names catchy and descriptive
- Keep summaries to one engaging sentence (max 20 words)
- Consider the location's history, culture, food, architecture, nature, shopping, nightlife, and local experiences
- Make each theme distinct and appealing to different traveler interests
- Ensure the JSON is properly formatted with double quotes
- Choose emojis that are relevant and help visualize the theme at a glance

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
        "address": "Full address of the POI"
    }},
    {{
        "poi_title": "Name of the POI",
        "address": "Full address of the POI"
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
        List of dictionaries containing poi_title and address

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
            if not isinstance(poi, dict) or 'poi_title' not in poi or 'address' not in poi:
                raise Exception("Invalid POI format in response")

        return pois

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")

async def validate_user_request_guardrail(user_address: str, max_time: str, distance: str, custom_message: str) -> bool:
    """
    Validate if the user's custom tour request makes sense for their current location.

    Args:
        user_address: The user's current location address
        max_time: Maximum time available for the tour
        distance: Maximum distance willing to travel
        custom_message: User's custom request/preferences

    Returns:
        True if the request is legitimate and makes sense, False otherwise

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

    # Create the validation prompt
    prompt = f"""You are a location and tour validation expert. Your job is to determine if a user's tour request makes sense given their current location.

User's Current Location: {user_address}

User's Tour Request:
- Maximum Time Available: {max_time}
- Maximum Distance Willing to Travel: {distance}
- Custom Preferences/Request: {custom_message}

Please analyze if this tour request is legitimate and makes sense for the user's location. Consider:

1. Geographic Relevance: Does the custom request relate to things that could reasonably be found in or near the user's location?
   - Example: "chicken rice tour" in Singapore = VALID
   - Example: "chicken rice tour" in New York = INVALID (chicken rice is specific to Singapore/Malaysia)
   - Example: "pizza tour" in New York = VALID
   - Example: "sushi tour" in Tokyo = VALID

2. Feasibility: Can the request be fulfilled within the given time and distance constraints for that location?

3. Cultural/Geographic Match: Does the request match the cultural or geographic context of the location?
   - Example: "surfing tour" in Hawaii = VALID
   - Example: "surfing tour" in landlocked Switzerland = INVALID
   - Example: "temple tour" in Kyoto = VALID
   - Example: "beach tour" in Paris = INVALID (no beaches in Paris)

Return your answer in this EXACT JSON format, nothing else:
{{
    "valid": true or false,
    "reason": "Brief explanation of why this is valid or invalid"
}}

IMPORTANT: Return ONLY the JSON object, no additional text."""

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
        result = json.loads(response_text)

        # Validate response structure
        if 'valid' not in result:
            raise Exception("Invalid response format from Gemini API")

        # Log the validation reason
        print(f"🛡️ Guardrail validation for '{custom_message}' at '{user_address}': {result.get('valid')}")
        print(f"   Reason: {result.get('reason', 'No reason provided')}")

        return result.get('valid', False)

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse guardrail response as JSON: {str(e)}")
        # Default to False if we can't parse the response
        return False
    except Exception as e:
        print(f"❌ Error calling Gemini API for guardrail: {str(e)}")
        # Default to False on error for safety
        return False


async def order_pois_for_tour(pois: List[Dict[str, str]], user_address: str, max_time: str, distance: str, theme: str, feedback: Optional[str] = None) -> List[Dict]:
    """
    Order POIs optimally for a tour based on constraints and proximity.

    Args:
        pois: List of POI dictionaries with poi_title and poi_address
        user_address: User's starting location
        max_time: Maximum time available for the tour
        distance: Maximum distance willing to travel
        theme: Tour theme/custom message
        feedback: Feedback from previous attempt (e.g. "Too long", "Too far")

    Returns:
        List of ordered POIs with order field added

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

    # Create POI list for prompt
    poi_list_str = ""
    for i, poi in enumerate(pois, 1):
        poi_list_str += f"{i}. {poi.get('poi_title', 'Unknown')} - {poi.get('address', 'Unknown')}\n"

    feedback_text = ""
    if feedback:
        feedback_text = f"\nIMPORTANT FEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}\nPlease adjust the plan to address this feedback. You may remove less important POIs if necessary to meet constraints.\n"

    # Create the ordering prompt
    prompt = f"""You are an expert tour planner. Given a list of Points of Interest (POIs) and constraints, determine the optimal order to visit them.

Starting Location: {user_address}

Tour Theme: {theme}

Constraints:
- Maximum Time: {max_time}
- Maximum Distance: {distance}
{feedback_text}
POIs to visit:
{poi_list_str}

Please determine the most efficient order to visit these POIs considering:
1. Proximity to starting location and each other (minimize travel distance)
2. Logical flow that makes sense for the tour theme
3. Time constraints (can all POIs be visited within the time limit?)
4. Creating a good tour experience (avoid excessive backtracking)

Return your answer in this EXACT JSON format, nothing else:
{{
    "ordered_pois": [
        {{
            "original_index": 1,
            "poi_title": "POI Title",
            "poi_address": "POI Address",
            "order": 1,
            "reasoning": "Brief reason for this position"
        }},
        {{
            "original_index": 2,
            "poi_title": "POI Title",
            "poi_address": "POI Address",
            "order": 2,
            "reasoning": "Brief reason for this position"
        }}
    ]
}}

IMPORTANT: 
- Use the original_index to match POIs from the input list (starting from 1)
- The "order" field should be the sequence in the tour (1 = first stop, 2 = second stop, etc.)
- Return ONLY the JSON object, no additional text."""

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
        result = json.loads(response_text)

        if 'ordered_pois' not in result:
            raise Exception("Invalid response format from Gemini API")

        ordered_pois = result['ordered_pois']

        print(f"🗺️ Tour order planned for {len(ordered_pois)} POIs")
        for poi in ordered_pois:
            print(f"   {poi.get('order')}. {poi.get('poi_title')} - {poi.get('reasoning', 'No reason')}")

        return ordered_pois

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Gemini ordering response as JSON: {str(e)}")
        # Fallback: return POIs in original order
        return [{"original_index": i+1, "poi_title": poi.get('poi_title'), "poi_address": poi.get('poi_address'), "order": i+1} 
                for i, poi in enumerate(pois)]
    except Exception as e:
        print(f"❌ Error calling Gemini API for POI ordering: {str(e)}")
        # Fallback: return POIs in original order
        return [{"original_index": i+1, "poi_title": poi.get('poi_title'), "poi_address": poi.get('poi_address'), "order": i+1} 
                for i, poi in enumerate(pois)]
