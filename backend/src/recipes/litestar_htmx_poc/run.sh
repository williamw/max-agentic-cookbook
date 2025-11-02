#!/bin/bash
# Quick start script for Litestar + HTMX POC

set -e

echo "🚀 Starting Litestar + HTMX POC..."
echo ""
echo "The app will be available at: http://localhost:8012"
echo ""
echo "Make sure you have COOKBOOK_ENDPOINTS configured:"
echo "export COOKBOOK_ENDPOINTS='[{\"id\":\"localhost\",\"baseUrl\":\"http://localhost:8000/v1\",\"apiKey\":\"EMPTY\"}]'"
echo ""

# Load .env if it exists
if [ -f .env ]; then
    echo "Loading environment from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the app
cd "$(dirname "$0")/../../.."
exec .venv/bin/python -m src.recipes.litestar_htmx_poc.app
