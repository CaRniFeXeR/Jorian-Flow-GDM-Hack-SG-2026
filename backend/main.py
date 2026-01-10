import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from routes import tts, tour

app = FastAPI(
    title="Jorian Flow Tour API",
    description="API for generating thematic tour options based on location",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API v1 router
api_v1_router = APIRouter(prefix="/api/v1")

# Register routers under /api/v1
api_v1_router.include_router(tts.router, prefix="/tts", tags=["TTS"])
api_v1_router.include_router(tour.router, tags=["Tour"])

# Mount the v1 API router
app.include_router(api_v1_router)

# Expose OpenAPI schema at /api/v1/openapi.json
@app.get("/api/v1/openapi.json", include_in_schema=False)
async def openapi_json():
    from fastapi.openapi.utils import get_openapi
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema


def get_endpoints_from_routes(app: FastAPI) -> dict:
    """Auto-generate endpoint descriptions from FastAPI routes."""
    from fastapi.routing import APIRoute
    
    endpoints = {}
    
    for route in app.routes:
        # Only process APIRoute instances (skip static routes, etc.)
        if not isinstance(route, APIRoute):
            continue
        
        # Skip routes that are not included in the schema
        if not route.include_in_schema:
            continue
        
        # Get the path
        path = route.path
        
        # Get HTTP methods for the route
        methods = sorted(route.methods - {'HEAD', 'OPTIONS'})  # Exclude HEAD and OPTIONS
        
        # Skip if no methods or if it's a root/health route
        if not methods or path in ['/', '/health']:
            continue
        
        # Get description from route (prefer summary, fallback to docstring)
        description = ""
        if hasattr(route, 'summary') and route.summary:
            description = route.summary
        elif route.endpoint and hasattr(route.endpoint, '__doc__') and route.endpoint.__doc__:
            # Extract first line of docstring as description
            docstring = route.endpoint.__doc__.strip()
            if docstring:
                first_line = docstring.split('\n')[0].strip()
                description = first_line
        
        # Format endpoint info
        for method in methods:
            method_str = method
            if description:
                endpoint_info = f"{method_str} - {description}"
            else:
                endpoint_info = method_str
            
            # Store endpoint info (combine if multiple methods exist)
            if path in endpoints:
                # Check if this method is already listed
                if method_str not in endpoints[path]:
                    endpoints[path] = f"{endpoints[path]}, {endpoint_info}"
            else:
                endpoints[path] = endpoint_info
    
    return endpoints


@app.get("/")
async def root():
    endpoints = get_endpoints_from_routes(app)
    return {
        "message": "Welcome to Jorian Flow Tour API",
        "version": app.version,
        "endpoints": endpoints
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level = "debug", access_log=True)
