#!/bin/bash
# ============================================================================
# AZURE STARTUP SCRIPT - Resume Formatter Backend
# ============================================================================
# This script is executed by Azure App Service when your application starts
# ============================================================================

echo "=========================================="
echo "🚀 Starting Resume Formatter Backend"
echo "=========================================="

# Download spaCy language model if not already present
echo "📦 Checking spaCy language model..."
python -m spacy download en_core_web_sm --quiet 2>/dev/null || echo "✅ spaCy model already installed"

# Start Gunicorn server
echo "🌐 Starting Gunicorn server..."
echo "   - Binding to: 0.0.0.0:8000"
echo "   - Workers: 2"
echo "   - Timeout: 600 seconds"
echo "=========================================="

# Start the application with Gunicorn
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 --access-logfile '-' --error-logfile '-' app:app
