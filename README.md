# DUDOXX Field Extraction System

A Python-based system for extracting structured fields from long-form text using the DUDOXX LLM API. The system efficiently processes large documents by chunking the text, processing chunks in parallel, and merging the results.

## Features

- **Efficient Text Chunking**: Split long documents into manageable chunks with configurable overlap to preserve context
- **Parallel Processing**: Process chunks concurrently to meet performance requirements
- **Accurate Field Extraction**: Use prompt engineering techniques to extract fields accurately
- **Flexible Output Formats**: Support for JSON, text, Markdown, CSV, and HTML output formats
- **Date Normalization**: Automatically normalize dates to a consistent format
- **Configurable via Environment**: All parameters can be configured via environment variables

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dudoxx-extractor.git
cd dudoxx-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the environment variables in `dudoxx-llm.env`:
```
DUDOXX_API_KEY=your_api_key
DUDOXX_BASE_URL=https://llm-proxy.dudoxx.com/v1
DUDOXX_MODEL_NAME=dudoxx
```

## Usage

### Basic Usage

Extract fields from a text file:

```bash
python main.py input.txt --fields "first_name,last_name,birthdate"
```

### Advanced Usage

```bash
python main.py input.txt \
  --fields "first_name,last_name,birthdate,address,phone,email" \
  --output "extracted_data" \
  --format json \
  --chunk-method paragraphs \
  --chunk-size 1500 \
  --chunk-overlap 200 \
  --max-threads 8 \
  --date-fields "birthdate" \
  --date-format "dd/mm/YYYY"
```

### Command-line Arguments

- `input_file`: Path to the input text file
- `--fields`: Comma-separated list of fields to extract
- `--output`: Path to the output file (without extension)
- `--format`: Output format (json, text, md, csv, html)
- `--chunk-method`: Method for chunking text (words, paragraphs)
- `--chunk-size`: Size of each chunk in words
- `--chunk-overlap`: Overlap between chunks in words
- `--max-threads`: Maximum number of worker threads
- `--date-fields`: Comma-separated list of date fields to normalize
- `--date-format`: Format for date fields
- `--unknown-value`: Value to use for unknown fields
- `--system-prompt`: System prompt to use

## Environment Configuration

All parameters can be configured via environment variables in the `dudoxx-llm.env` file:

```
# API Configuration
DUDOXX_API_KEY=your_api_key
DUDOXX_BASE_URL=https://llm-proxy.dudoxx.com/v1
DUDOXX_MODEL_NAME=dudoxx
DUDOXX_MEMORY_ENTRIES=5

# Chunking Configuration
DUDOXX_CHUNK_SIZE=1000
DUDOXX_CHUNK_OVERLAP=100
DUDOXX_MIN_CHUNK_SIZE=200

# Parallel Processing Configuration
DUDOXX_MAX_THREADS=5
DUDOXX_BATCH_SIZE=10

# API Request Configuration
DUDOXX_REQUEST_TIMEOUT=30
DUDOXX_MAX_RETRIES=3
DUDOXX_RETRY_DELAY=2

# Extraction Configuration
DUDOXX_DEFAULT_SYSTEM_PROMPT=You are an expert data extractor. Only output the fields requested, based solely on the given text.
DUDOXX_OUTPUT_FORMAT=json
DUDOXX_UNKNOWN_VALUE=unknown

# Date Formatting
DUDOXX_DATE_FORMAT=dd/mm/YYYY

# Logging Configuration
DUDOXX_DETAILED_LOGGING=true
DUDOXX_SAVE_PROMPTS=true
DUDOXX_LOG_LEVEL=INFO
```

## System Architecture

The system is organized into several modules:

```
dudoxx_extractor_project/
├── dudoxx-llm.env                 # Environment configuration
├── src/
│   ├── config/                    # Configuration module
│   │   ├── env_loader.py          # Load environment variables
│   │   └── settings.py            # Central settings with defaults
│   ├── api/                       # API module
│   │   └── dudoxx_client.py       # DUDOXX API client using OpenAI SDK
│   ├── chunking/                  # Chunking module
│   │   └── text_chunker.py        # Text chunking strategies
│   ├── extraction/                # Extraction module
│   │   ├── prompt_builder.py      # Build extraction prompts
│   │   └── field_extractor.py     # Extract fields from chunks
│   ├── processing/                # Processing module
│   │   └── parallel_processor.py  # Parallel processing of chunks
│   ├── merging/                   # Merging module
│   │   └── result_merger.py       # Merge results from chunks
│   └── utils/                     # Utilities
│       ├── formatters.py          # Format output
│       └── validators.py          # Validate extracted data
├── main.py                        # Main entry point
├── input_data/                    # Sample input data
└── output_results/                # Output results
```

### Processing Flow

1. **Input Acquisition**: Read the input text file
2. **Text Chunking**: Split the text into chunks with overlap
3. **Parallel Processing**: Process chunks in parallel using ThreadPoolExecutor
4. **Field Extraction**: Extract fields from each chunk using the DUDOXX LLM
5. **Result Merging**: Combine results from multiple chunks
6. **Validation and Normalization**: Validate and normalize the merged results
7. **Output Formatting**: Format the results in the specified format
8. **Output Delivery**: Save the formatted results to a file

## Examples

### Example 1: Extract Personal Information

```bash
python main.py input_data/sample1.txt \
  --fields "first_name,last_name,birthdate,gender,address,phone,email" \
  --output "patient_info" \
  --format json
```

Output (`output_results/patient_info.json`):
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "birthdate": "09/02/1949",
  "gender": "Male",
  "address": "123 Main St, Apt 4B, New York, NY 10001",
  "phone": "(555) 123-4567",
  "email": "john.smith@email.com"
}
```

### Example 2: Extract Resume Information

```bash
python main.py input_data/sample2.txt \
  --fields "name,email,phone,skills,education,work_experience" \
  --output "resume_info" \
  --format md
```

Output (`output_results/resume_info.md`):
```markdown
# Extracted Fields

**name**: Jane Doe
**email**: jane.doe@email.com
**phone**: (415) 555-7890

## skills
- JavaScript, TypeScript, Python, Java, SQL
- React, Angular, Vue.js, HTML5, CSS3, SASS
- Node.js, Express, Django, Spring Boot
- PostgreSQL, MongoDB, Redis, MySQL
- AWS, Docker, Kubernetes, CI/CD, Terraform

## education
- Master of Science in Computer Science, Stanford University, May 2015
- Bachelor of Science in Computer Engineering, University of California, Berkeley, June 2013

## work_experience
- Senior Software Engineer, TechCorp Inc., March 2020 - Present
- Software Engineer, InnovateSoft, June 2017 - February 2020
- Junior Developer, StartupLaunch, August 2015 - May 2017
```

## Requirements

- Python 3.8+
- Required packages:
  - requests
  - python-dotenv
  - openai>=1.0.0
  - concurrent.futures (standard library)

## License

MIT License
