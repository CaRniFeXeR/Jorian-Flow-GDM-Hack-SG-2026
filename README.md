# AiTours

You're in Vienna for a conference, with just two hours to spare. You could follow the same crowded route to the Hofburg Palace… or you could step into the hidden world of Otto Wagner, the architect who shaped the city's soul. But how? Tour guides are booked, audio tours are generic, and Google Maps just shows you dots on a map.

Most travel apps give you the same old tourist trails. But what if you want to explore the city through the eyes of a local historian, an architect, or even a fictional character?

Meet AiTours—the first AI-powered app that crafts bespoke walking tours in minutes. Tell us your interest (like "Otto Wagner's secret Vienna"), your time (2 hours), and your pace (no more than 5km), and we'll generate a tour that feels like it was made just for you.

Open the app, and your custom tour appears: a beautifully illustrated map, a narrative that unfolds as you walk, and curated stories at every stop—like a private guide in your pocket. No research, no planning, just adventure.

Unlike static audio guides or generic walking tours, AiTours uses real-time AI to weave together history, architecture, and local secrets into a seamless, personalized experience.

AiTours isn't just a map—it's your passport to the stories that make a city come alive. Ready to explore like a local?

---

## Overview

AiTours is a full-stack web application that generates personalized walking tours using AI. The system combines Google's Gemini AI for intelligent content generation with Google Maps APIs for location services and verification, creating unique, narrative-driven tours tailored to user preferences, time constraints, and interests.

## Architecture

The project is structured as a modern full-stack application with a clear separation between frontend and backend:

```
.
├── backend/          # FastAPI Python backend
├── frontend/         # React + TypeScript frontend
└── README.md         # This file
```

### Backend Structure

The backend is built with **FastAPI** and follows a service-oriented architecture:

```
backend/
├── main.py                          # FastAPI application entry point
├── routes/                          # API route handlers
│   ├── tour.py                     # Tour generation endpoints
│   └── tts.py                      # Text-to-speech endpoints
├── services/                        # Business logic services
│   ├── gemini_service.py           # Gemini AI integration
│   ├── maps_service.py             # Google Maps API integration
│   ├── poi_service.py              # POI management
│   ├── tour_service.py             # Tour data management
│   ├── tour_orchestration_service.py  # Tour generation orchestration
│   └── tts_service.py              # Text-to-speech generation
├── database/                        # Data persistence layer
│   ├── database_base.py            # Database abstraction
│   ├── tour.py                     # Tour repository
│   └── tts_storage.py              # TTS cache repository
└── schemas/                         # Pydantic data models
    └── tour.py                     # Tour data schemas
```

**Key Backend Technologies:**
- FastAPI (async web framework)
- Pydantic (data validation)
- TinyDB (lightweight JSON database)
- Python 3.x

### Frontend Structure

The frontend is built with **React** and **TypeScript** using modern tooling:

```
frontend/
├── src/
│   ├── components/                 # React components
│   │   ├── Map/                   # Map visualization components
│   │   ├── Tour/                  # Tour display components
│   │   ├── Audio/                 # Audio playback components
│   │   ├── Onboarding/            # User onboarding flow
│   │   └── UI/                    # Reusable UI components
│   ├── context/                   # React context providers
│   │   ├── TourContext.tsx        # Tour state management
│   │   └── OnboardingContext.tsx  # Onboarding state
│   ├── client/                    # Auto-generated API client
│   └── App.tsx                    # Main application component
├── package.json                   # Dependencies and scripts
└── vite.config.ts                 # Vite build configuration
```

**Key Frontend Technologies:**
- React 19
- TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- @vis.gl/react-google-maps (Google Maps integration)
- Framer Motion (animations)

## AI Agent Usage

AiTours leverages **Google Gemini AI** as an intelligent agent to orchestrate the tour generation process. The agent performs multiple roles:

### 1. **Theme Generation Agent**
- Analyzes user location and generates creative, thematic tour options
- Considers local history, culture, architecture, and unique characteristics
- Uses: `gemini-3-flash-preview` model

### 2. **POI Discovery Agent**
- Generates relevant Points of Interest based on user constraints (time, distance, interests)
- Filters and selects POIs that can realistically be visited within constraints
- Uses: `gemini-3-flash-preview` model

### 3. **Route Optimization Agent**
- Orders POIs optimally considering walking distance, time constraints, and thematic flow
- Iteratively refines routes based on feedback (e.g., "too long", "too far")
- Ensures tours are practical and enjoyable
- Uses: `gemini-3-flash-preview` model

### 4. **Content Generation Agent**
- **Tour Introductions**: Creates engaging opening narratives that set the theme
- **Narrative Stories**: Generates rich, contextual stories for each POI that weave together into a cohesive narrative
- Tailors content to user interests and the chosen theme
- Uses: `gemini-3-flash-preview` model

### 5. **Guardrail Agent**
- Validates user requests to ensure safety and appropriateness
- Filters out potentially problematic or unrealistic requests
- Uses: `gemini-3-flash-preview` model

The agent orchestrates these tasks through the `TourOrchestrationService`, which manages the multi-step tour generation pipeline, ensuring each step completes successfully before proceeding to the next.

## Google Products Utilized

AiTours integrates multiple Google products to deliver a complete experience:

### 1. **Google Gemini AI** 🧠
- **Models Used:**
  - `gemini-3-flash-preview` - Primary model for content generation, POI discovery, route optimization, and guardrails
  - `gemini-2.5-flash-preview-tts` - Text-to-speech model for audio narration
- **Use Cases:**
  - Theme generation
  - POI discovery and recommendation
  - Route optimization
  - Narrative story generation
  - Tour introduction creation
  - Request validation (guardrails)
  - Text-to-speech conversion

### 2. **Google Maps Platform** 🗺️
- **APIs Used:**
  - **Geocoding API** - Converts coordinates to addresses and vice versa
  - **Places API** - Verifies POIs exist, retrieves place details, photos, and metadata
  - **Directions API** - Calculates routes and walking distances between POIs
- **Frontend Integration:**
  - **@vis.gl/react-google-maps** - React components for interactive map visualization
- **Use Cases:**
  - Reverse geocoding (coordinates → address)
  - Forward geocoding (address → coordinates)
  - POI verification (filtering out non-existent locations)
  - Place detail enrichment (photos, descriptions, GPS coordinates)
  - Route calculation and distance estimation
  - Interactive map rendering with markers and routes

### Integration Flow

1. **User Input** → Frontend captures preferences (location, time, distance, interests)
2. **Guardrail Validation** → Gemini validates the request
3. **POI Generation** → Gemini generates candidate POIs based on constraints
4. **POI Verification** → Google Maps Places API verifies POIs exist and are accessible
5. **Route Optimization** → Gemini orders POIs optimally
6. **Enrichment** → Google Maps enriches POIs with photos, coordinates, and details
7. **Content Generation** → Gemini creates narratives and introductions
8. **Audio Generation** → Gemini TTS converts narratives to audio
9. **Visualization** → Google Maps renders the interactive tour map

## Getting Started

### Prerequisites

- Python 3.8+ (for backend)
- Node.js 18+ and npm (for frontend)
- Google Gemini API key
- Google Maps API key (with Geocoding, Places, and Directions APIs enabled)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Create .env file
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

4. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/api/v1/openapi.json`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
# Create .env file
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
VITE_API_BASE_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5174`

### Generating API Client

The frontend uses an auto-generated API client from the OpenAPI schema:

```bash
cd frontend
npm run generate-client
```

This generates TypeScript types and client code in `src/client/` from the backend's OpenAPI specification.

## API Keys Setup

### Getting a Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and paste it into your `.env` file

### Getting a Google Maps API Key

1. Visit https://console.cloud.google.com/google/maps-apis/
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Geocoding API** (for address conversion)
   - **Places API** (for POI verification and details)
   - **Directions API** (for route calculation)
4. Go to Credentials and create an API key
5. Copy and paste it into your `.env` file (both backend and frontend)

## Features

- 🎯 **Personalized Tour Generation** - AI-powered tours tailored to your interests, time, and distance constraints
- 🗺️ **Interactive Maps** - Beautiful Google Maps visualization with routes and markers
- 📖 **Narrative Storytelling** - Rich, contextual stories at each stop that weave together into a cohesive narrative
- 🎧 **Audio Narration** - Text-to-speech audio for hands-free tour experience
- ✅ **POI Verification** - Google Maps integration ensures all suggested locations actually exist
- 🔄 **Route Optimization** - AI-optimized routes that respect time and distance constraints
- 🎨 **Beautiful UI** - Modern, responsive interface built with React and Tailwind CSS

## License

See LICENSE file for details.
