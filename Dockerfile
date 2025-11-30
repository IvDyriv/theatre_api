# Use slim Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies (for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run wait_for_db before starting server
CMD ["sh", "-c", "python manage.py wait_for_db && python manage.py runserver 0.0.0.0:8000"]
