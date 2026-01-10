# Jorian Flow Tour API

FastAPI backend service for generating thematic tour options and Points of Interest (POIs) using Google's Gemini AI and Google Maps API.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_actual_google_maps_api_key_here
```

**To get a Gemini API key:**
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and paste it into your `.env` file

**To get a Google Maps API key:**
1. Visit https://console.cloud.google.com/google/maps-apis/
2. Create a new project or select an existing one
3. Enable the "Geocoding API"
4. Go to Credentials and create an API key
5. Copy and paste it into your `.env` file

### 3. Run the Server

```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Endpoints

### POST /theme_options

Generate thematic tour options for a given location.

**Request Body:**
```json
{
  "address": "Orchard Road, Singapore"
}
```

**Response:**
```json
{
  "themes": {
    "Historical Heritage Tour": "Explore the colonial architecture and historical landmarks along this iconic street",
    "Shopping & Fashion Tour": "Discover luxury brands and modern shopping centers in Singapore's premier retail district",
    "Cultural Fusion Tour": "Experience the blend of traditional and contemporary Asian culture",
    "Culinary Adventure Tour": "Savor diverse cuisines from hawker favorites to fine dining experiences",
    "Nature & Urban Escapes": "Find hidden green spaces and parks amidst the bustling city center"
  }
}
```

### POST /generate_poi

Generate Points of Interest (POIs) based on user coordinates and constraints.

This endpoint performs two steps:
1. Converts latitude/longitude to a human-readable address using Google Maps Geocoding API
2. Generates relevant POIs using Gemini API based on the address and user constraints

**Request Body:**
```json
{
  "latitude": 1.3048,
  "longitude": 103.8318,
  "constraints": {
    "time": "2 hours",
    "distance": "5 km",
    "user_custom_info": "I love historical sites and local food"
  }
}
```

**Response:**
```json
{
  "user_address": "Orchard Road, Singapore 238801",
  "pois": [
    {
      "poi_title": "Singapore Botanic Gardens",
      "poi_address": "1 Cluny Rd, Singapore 259569"
    },
    {
      "poi_title": "ION Orchard",
      "poi_address": "2 Orchard Turn, Singapore 238801"
    },
    {
      "poi_title": "National Museum of Singapore",
      "poi_address": "93 Stamford Rd, Singapore 178897"
    },
    {
      "poi_title": "Maxwell Food Centre",
      "poi_address": "1 Kadayanallur St, Singapore 069184"
    }
  ]
}
```

**Constraints:**
- `time`: Time available for visiting POIs (e.g., "2 hours", "half day", "full day")
- `distance`: Maximum distance willing to travel (e.g., "1 km", "5 miles", "walking distance")
- `user_custom_info`: Additional preferences like interests, dietary restrictions, accessibility needs, etc.

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Project Structure

```
backend/
├── main.py              # FastAPI application and endpoints
├── gemini_service.py    # Gemini API integration and prompt templates
├── maps_service.py      # Google Maps API integration (reverse geocoding)
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .env                 # Your environment variables (not in git)
└── README.md            # This file
```

## Prompt Templates

### Theme Options Prompt

The `get_prompt_template()` function in `gemini_service.py` is designed to generate creative, location-specific tour themes. It instructs Gemini to:
- Analyze the location's unique characteristics
- Generate 5 distinct thematic tour options
- Return structured JSON output
- Create engaging, concise descriptions

### POI Generation Prompt

The `get_poi_prompt_template()` function in `gemini_service.py` generates personalized POI recommendations. It instructs Gemini to:
- Consider user location and constraints (time, distance, preferences)
- Generate 5-10 relevant POIs that can be visited within constraints
- Include diverse POI types (attractions, restaurants, parks, etc.)
- Return structured JSON array with poi_title and poi_address
- Order POIs by relevance and proximity

You can customize both prompt templates to adjust the number of results, response format, or generation guidelines.
