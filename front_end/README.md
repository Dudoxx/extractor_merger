# DUDOXX Field Extractor API

A FastAPI frontend for the DUDOXX field extraction system. This API provides endpoints for extracting structured information from long-form text using LLM-based extraction.

## Features

- **Field Extraction**: Extract structured fields from unstructured text
- **Parallel Processing**: Process large texts efficiently using parallel processing
- **Authentication**: Secure API access with token-based authentication
- **Comprehensive Logging**: Detailed logging for requests, responses, and errors
- **Error Handling**: Robust error handling with detailed error responses
- **Documentation**: Interactive API documentation with examples
- **Health Checks**: Endpoint for checking the health of the service
- **Containerization**: Docker support for easy deployment

## API Endpoints

- **POST /api/v1/extract**: Extract fields from text
- **POST /api/v1/extract/file**: Extract fields from an uploaded file
- **GET /api/v1/health**: Check the health of the service
- **GET /api/v1/docs**: Get API documentation

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Dudoxx/extractor_merger.git
cd extractor_merger
```

2. Install dependencies:

```bash
cd front_end
pip install -r requirements.txt
```

3. Run the API:

```bash
python run.py
```

The API will be available at http://localhost:8000.

### Using Docker

1. Build the Docker image:

```bash
cd front_end
docker build -t dudoxx-extractor-api .
```

2. Run the Docker container:

```bash
docker run -p 8000:8000 dudoxx-extractor-api
```

## API Usage

### Authentication

All requests to the `/api/v1/extract` endpoint require authentication. Include the API token in the `Authorization` header:

```
Authorization: Bearer sk-dudoxx-2025
```

### Example Requests

#### Extract from Text

```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-dudoxx-2025" \
  -d '{
    "text": "Patient: John Smith, DOB: 09/02/1949...",
    "fields": ["first_name", "last_name", "birthdate"],
    "chunking_method": "words",
    "chunk_size": 500,
    "chunk_overlap": 100,
    "max_workers": 5,
    "output_format": "json"
  }'
```

#### Extract from File

```bash
curl -X POST http://localhost:8000/api/v1/extract/file \
  -H "Authorization: Bearer sk-dudoxx-2025" \
  -F "file=@/path/to/your/file.txt" \
  -F "fields=first_name,last_name,birthdate" \
  -F "chunking_method=words" \
  -F "chunk_size=500" \
  -F "chunk_overlap=100" \
  -F "max_workers=5" \
  -F "output_format=json"
```

### Example Response

```json
{
  "status": "success",
  "request_id": "f8d7e6c5-b4a3-42d1-9f0e-8c7b6a5d4e3c",
  "processing_time": 1.25,
  "extracted_fields": {
    "first_name": "John",
    "last_name": "Smith",
    "birthdate": "09/02/1949"
  },
  "metrics": {
    "chunks_processed": 4,
    "llm_calls": 4,
    "processing_time": 1.25
  }
}
```

## Configuration

The API can be configured using environment variables in the `dudoxx-llm.env` file. Key configuration options include:

- `DUDOXX_API_KEY`: API key for the DUDOXX LLM API
- `DUDOXX_EXTRACTOR_TOKEN`: API token for authentication
- `DUDOXX_CHUNK_SIZE`: Size of each chunk in words
- `DUDOXX_CHUNK_OVERLAP`: Overlap between chunks in words
- `DUDOXX_MAX_THREADS`: Maximum number of worker threads
- `DUDOXX_DEFAULT_SYSTEM_PROMPT`: Default system prompt for the LLM
- `DUDOXX_OUTPUT_FORMAT`: Default output format
- `DUDOXX_UNKNOWN_VALUE`: Value to use for unknown fields
- `DUDOXX_DATE_FORMAT`: Format for date fields

## License

This project is licensed under the MIT License - see the LICENSE file for details.
