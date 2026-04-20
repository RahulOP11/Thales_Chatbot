# Use Python 3.10 slim as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Cloud Run sets the PORT env variable automatically, defaults to 8080 usually)
ENV PORT=8000
EXPOSE $PORT

# Command to run the FastAPI application natively
CMD ["python", "main.py"]
