# Jorian Flow Tour API

FastAPI backend service for generating thematic tour options using Google's Gemini AI.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your Gemini API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

To get a Gemini API key:
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and paste it into your `.env` file

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
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment variables
└── README.md           # This file
```

## Prompt Template

The prompt template in `gemini_service.py` is designed to generate creative, location-specific tour themes. It instructs Gemini to:
- Analyze the location's unique characteristics
- Generate 5 distinct thematic tour options
- Return structured JSON output
- Create engaging, concise descriptions

You can customize the prompt template in the `get_prompt_template()` function to adjust the number of themes, response format, or generation guidelines.
