#!/bin/bash
set -e

echo "Removing existing openapi.json..."
rm -f openapi.json

echo "Downloading OpenAPI schema from backend..."
wget http://localhost:8000/openapi.json -O openapi.json

echo "Modifying OpenAPI schema..."
node modify-openapi-operationids.js

echo "Generating TypeScript client..."
npm run generate-client

echo "Client generation complete!"
