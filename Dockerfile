# Use Python 3.10 slim as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model into the Docker image cache.
# This strictly prevents Cloud Run from timing out or crashing by attempting to download massive files at startup.
RUN python -c "from langchain_community.embeddings import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-small', model_kwargs={'device': 'cpu'})"

# Copy the rest of the application code
COPY . .

# Expose generic port
ENV PORT=8080
EXPOSE $PORT

# Command to unequivocally route to exactly the correct Cloud Run Port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
