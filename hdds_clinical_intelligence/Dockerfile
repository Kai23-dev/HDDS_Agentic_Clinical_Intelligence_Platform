# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install
# Copy the rest of the frontend source and build it
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the Python Backend and Serve
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
COPY . .

# Copy the built React app from Stage 1 into the backend's expected directory
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Expose the single FastAPI port
EXPOSE 8000

# Run uvicorn (which now serves both API and React)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
