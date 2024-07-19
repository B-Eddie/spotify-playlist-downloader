# Use a base Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install spotdl
RUN pip install spotdl

# Install other Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code into the container
COPY . /app/

# Expose the Flask app port
EXPOSE 8080

# Command to run the Flask application
CMD ["python", "main.py", "--host=0.0.0.0", "--port=8080"]
