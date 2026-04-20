# Use Python 3.10 slim as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set explicit caching directories so the Cloud Run environment retains access to the models offline
ENV HF_HOME=/app/.hf_cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/.hf_cache
RUN mkdir -p /app/.hf_cache && chmod 777 /app/.hf_cache

# Pre-download the embedding model strictly into the persistent explicit cache directory
RUN python -c "from langchain_community.embeddings import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-small', model_kwargs={'device': 'cpu'})"

# Copy the rest of the application code
COPY . .

# Expose generic port
ENV PORT=8080
EXPOSE $PORT

# Command to unequivocally route to exactly the correct Cloud Run Port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
