#!/bin/bash

# Exit on error
set -e


echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🚀 Starting FastAPI server on port 5050..."
uvicorn main:app --host 0.0.0.0 --port 5050