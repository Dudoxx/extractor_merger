FROM python:3.9-slim

WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY ../requirements.txt ./core_requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r core_requirements.txt

# Copy application code
COPY . .
COPY ../src ./src
COPY ../dudoxx-llm.env .

# Create necessary directories
RUN mkdir -p logs input_data output_results

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
