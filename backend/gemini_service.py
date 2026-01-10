import os
import json
import google.generativeai as genai
from typing import Dict


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
