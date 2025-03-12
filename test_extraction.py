#!/usr/bin/env python3
"""
Test script for the DUDOXX field extraction system.
This script demonstrates how to use the system without making actual API calls.
"""
import os
import json
import time
import argparse
from pathlib import Path
from src.chunking.text_chunker import chunk_text, chunk_text_by_paragraphs
from src.merging.result_merger import merge_results
from src.utils.formatters import format_output
from src.utils.validators import validate_and_normalize
from src.config import settings
from src.utils.logging_utils import get_logger, log_api_call

# Get logger
logger = get_logger()

# Create logs directory if it doesn't exist
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Mock extraction function to simulate API calls
def mock_extract_fields(chunk, fields, chunk_index=None):
    """
    Mock function to simulate field extraction without making API calls.
    
    Args:
        chunk (str): Text chunk
        fields (list): List of fields to extract
        chunk_index (int, optional): The index of the chunk being processed. Used for logging.
        
    Returns:
        dict: Extracted fields and values
    """
    # Log the chunk processing
    print(f"Processing chunk {chunk_index if chunk_index is not None else 'unknown'}")
    print(f"Chunk content (first 100 chars): {chunk[:100]}")
    logger.info(f"Processing chunk {chunk_index if chunk_index is not None else 'unknown'}")
    
    # Simulate API call
    start_time = time.time()
    time.sleep(0.1)  # Simulate API latency
    duration = time.time() - start_time
    
    # Initialize result with unknown values
    result = {field: settings.UNKNOWN_VALUE for field in fields}
    
    # Create a mock prompt and response for logging
    mock_prompt = f"Extract the following fields from the text: {', '.join(fields)}.\nText: {chunk[:100]}..."
    mock_response = {
        "id": f"mock-{time.time()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "dudoxx-mock",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(result, indent=2)
                },
                "finish_reason": "stop"
            }
        ]
    }
    
    # Log the API call
    log_api_call(mock_prompt, mock_response, duration, chunk_index)
    
    # Simulate different values from different chunks for the sample_duplicates.txt file
    
    # Section 1 format
    if 'first_name' in fields and 'Name: John' in chunk:
        result['first_name'] = 'John'
    if 'last_name' in fields and 'Name: John Smith' in chunk:
        result['last_name'] = 'Smith'
    if 'birthdate' in fields and 'Date of Birth: February 9th' in chunk:
        result['birthdate'] = '09/02/1949'
    if 'gender' in fields and 'Gender: Male' in chunk:
        result['gender'] = 'Male'
    if 'address' in fields and '123 Main St, New York' in chunk:
        result['address'] = '123 Main St, New York, NY 10001'
    if 'phone' in fields and '(555) 123-4567' in chunk:
        result['phone'] = '(555) 123-4567'
    if 'email' in fields and 'john.smith@email.com' in chunk:
        result['email'] = 'john.smith@email.com'
    
    # Section 2 format (different formatting)
    if 'first_name' in fields and 'Patient Name: John' in chunk:
        result['first_name'] = 'John'
    if 'last_name' in fields and 'Patient Name: John Smith' in chunk:
        result['last_name'] = 'Smith'
    if 'birthdate' in fields and 'DOB: 02/09/1949' in chunk:
        result['birthdate'] = '02/09/1949'  # Different format
    if 'gender' in fields and 'Gender: M' in chunk:
        result['gender'] = 'M'  # Different format
    if 'address' in fields and '123 Main Street, Apt 4B' in chunk:
        result['address'] = '123 Main Street, Apt 4B, New York, NY 10001'  # More complete
    if 'phone' in fields and 'Contact: 555-123-4567' in chunk:
        result['phone'] = '555-123-4567'  # Different format
    if 'email' in fields and 'johnsmith@email.com' in chunk:
        result['email'] = 'johnsmith@email.com'  # Different format
    
    # Resume fields
    if 'name' in fields and 'JANE DOE' in chunk:
        result['name'] = 'Jane Doe'
    if 'email' in fields and 'jane.doe@email.com' in chunk:
        result['email'] = 'jane.doe@email.com'
    if 'phone' in fields and '(415) 555-7890' in chunk:
        result['phone'] = '(415) 555-7890'
    
    # List fields - Medical History from different sections
    if 'medical_history' in fields and 'Medical History:' in chunk:
        result['medical_history'] = [
            'Type 2 Diabetes (diagnosed March 15, 2010)',
            'Hypertension since 2005',
            'Knee replacement surgery (July 12, 2018)'
        ]
    
    if 'medical_history' in fields and 'Additional Medical History:' in chunk:
        result['medical_history'] = [
            'Diagnosed with Type 2 Diabetes (March 15, 2010)',  # Same info, different format
            'High blood pressure (Hypertension) since 2005',    # Same info, different format
            'Underwent knee replacement surgery on July 12, 2018',  # Same info, different format
            'Appendectomy in 1985'  # New info only in this section
        ]
    
    if 'skills' in fields and 'SKILLS' in chunk:
        result['skills'] = [
            'JavaScript, TypeScript, Python, Java, SQL',
            'React, Angular, Vue.js, HTML5, CSS3, SASS',
            'Node.js, Express, Django, Spring Boot',
            'PostgreSQL, MongoDB, Redis, MySQL',
            'AWS, Docker, Kubernetes, CI/CD, Terraform'
        ]
    
    if 'education' in fields and 'EDUCATION' in chunk:
        result['education'] = [
            'Master of Science in Computer Science, Stanford University, May 2015',
            'Bachelor of Science in Computer Engineering, University of California, Berkeley, June 2013'
        ]
    
    if 'work_experience' in fields and 'WORK EXPERIENCE' in chunk:
        result['work_experience'] = [
            'Senior Software Engineer, TechCorp Inc., March 2020 - Present',
            'Software Engineer, InnovateSoft, June 2017 - February 2020',
            'Junior Developer, StartupLaunch, August 2015 - May 2017'
        ]
    
    return result

def main():
    """Main entry point for the test script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Test the DUDOXX field extraction system.')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--fields', required=True, help='Comma-separated list of fields to extract')
    parser.add_argument('--output', help='Path to the output file (without extension)')
    parser.add_argument('--format', choices=['json', 'text', 'md', 'csv', 'html'], default='json', 
                        help='Output format')
    parser.add_argument('--chunk-method', choices=['words', 'paragraphs'], default='words',
                        help='Method for chunking text')
    
    args = parser.parse_args()
    
    # Parse fields
    fields = [field.strip() for field in args.fields.split(',')]
    
    # Ensure input_data directory exists
    os.makedirs('input_data', exist_ok=True)
    
    # Ensure output_results directory exists
    os.makedirs('output_results', exist_ok=True)
    
    # Determine input file path
    if os.path.isabs(args.input_file):
        input_path = args.input_file
    else:
        input_path = os.path.join('input_data', args.input_file)
    
    # Determine output file path
    if args.output:
        if os.path.isabs(args.output):
            output_base = args.output
        else:
            output_base = os.path.join('output_results', args.output)
    else:
        output_base = os.path.join('output_results', os.path.splitext(os.path.basename(args.input_file))[0])
    
    # Read input text
    print(f"Reading input file: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # For sample_duplicates.txt, use manual chunking to simulate the scenario we want to test
    if args.input_file == 'sample_duplicates.txt' or args.input_file == 'input_data/sample_duplicates.txt':
        print("Using manual chunking for sample_duplicates.txt...")
        chunks = [
            # Chunk 1: Section 1 with personal information
            """Patient Medical Record - Duplicate Information Test

Personal Information (Section 1):
Name: John Smith
Date of Birth: February 9th, 1949
Gender: Male
Address: 123 Main St, New York, NY 10001
Phone: (555) 123-4567
Email: john.smith@email.com""",
            
            # Chunk 2: Medical History from Section 1
            """Medical History:
- Type 2 Diabetes (diagnosed March 15, 2010)
- Hypertension since 2005
- Knee replacement surgery (July 12, 2018)""",
            
            # Chunk 3: Section 2 with different formatting of personal information
            """Personal Information (Section 2 - Slightly Different Format):
Patient Name: John Smith
DOB: 02/09/1949
Gender: M
Address: 123 Main Street, Apt 4B, New York, NY 10001
Contact: 555-123-4567
Email Address: johnsmith@email.com""",
            
            # Chunk 4: Additional Medical History from Section 2
            """Additional Medical History:
- Diagnosed with Type 2 Diabetes (March 15, 2010)
- High blood pressure (Hypertension) since 2005
- Underwent knee replacement surgery on July 12, 2018
- Appendectomy in 1985 (not mentioned in first section)"""
        ]
    else:
        # Use normal chunking for other files
        print(f"Chunking text using {args.chunk_method} method...")
        if args.chunk_method == 'words':
            chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)  # Force smaller chunks for testing
        else:  # paragraphs
            # Force very small chunks by setting max_chunk_size to a small number of words
            chunks = chunk_text_by_paragraphs(text, max_chunk_size=50, chunk_overlap=10)  # Force smaller chunks for testing
    
    print(f"Text chunked into {len(chunks)} chunks")
    
    # Process chunks
    print("Processing chunks...")
    chunk_results = [mock_extract_fields(chunk, fields, idx) for idx, chunk in enumerate(chunks)]
    
    # Merge results
    print("Merging results...")
    merged_results = merge_results(chunk_results, fields)
    
    # Validate and normalize results
    validated_results = validate_and_normalize(merged_results, fields)
    
    # Format and save output
    output_format = args.format.lower()
    formatted_output = format_output(validated_results, output_format)
    
    # Save output in the specified format
    output_path = f"{output_base}.{output_format}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted_output)
    
    print(f"Test extraction complete. Results saved to {output_path}")
    
    # Also print the results to the console
    print("\nExtracted Fields:")
    if output_format == 'json':
        print(json.dumps(validated_results, indent=2))
    else:
        print(formatted_output)

if __name__ == "__main__":
    main()
