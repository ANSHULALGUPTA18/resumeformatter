# Resume Formatter - Single Container Deployment (Cost Optimized)
# Combines Frontend (React) + Backend (Flask) in one container

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for python-docx and ML models (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies (fixed)
COPY Backend/requirements.txt Backend/requirements_ml.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_ml.txt

# Copy backend code
COPY Backend/ ./backend/

# Copy frontend build (you'll build this before Docker)
COPY frontend/build/ ./frontend/

# Create necessary directories
RUN mkdir -p /app/backend/Output \
    /app/backend/Static/uploads/templates \
    /app/backend/Static/uploads/resumes

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "backend/app.py"]
