FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Run the application (use PORT from environment)
CMD uvicorn app.main:socket_app --host 0.0.0.0 --port ${PORT:-8000}
