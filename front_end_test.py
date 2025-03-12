#!/usr/bin/env python3
"""
Test script for the DUDOXX Field Extractor API.
Sends a sample text from the sample data folder to the API and displays the results.
"""
import os
import json
import time
import requests
from pprint import pprint

# API configuration
API_URL = "http://localhost:8000/api/v1/extract"
API_TOKEN = "sk-dudoxx-2025"  # From dudoxx-llm.env
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def read_sample_file(filename):
    """
    Read a sample file from the input_data directory.
    
    Args:
        filename (str): The name of the sample file
        
    Returns:
        str: The contents of the sample file
    """
    input_path = os.path.join("input_data", filename)
    with open(input_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_fields(text, fields, chunking_method="words", chunk_size=1000, chunk_overlap=100):
    """
    Extract fields from text using the API.
    
    Args:
        text (str): The text to extract fields from
        fields (list): List of fields to extract
        chunking_method (str, optional): Method for chunking text. Defaults to "words".
        chunk_size (int, optional): Size of each chunk in words. Defaults to 500.
        chunk_overlap (int, optional): Overlap between chunks in words. Defaults to 100.
        
    Returns:
        dict: The API response
    """
    # Prepare the request payload
    payload = {
        "text": text,
        "fields": fields,
        "chunking_method": chunking_method,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "max_workers": 5,
        "output_format": "json"
    }
    
    # Send the request to the API
    print(f"Sending request to {API_URL} with {len(text)} characters and {len(text.split())} words...")
    start_time = time.time()
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    elapsed_time = time.time() - start_time
    
    # Check if the request was successful
    if response.status_code == 200:
        print(f"Request successful! Response received in {elapsed_time:.2f} seconds.")
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    """Main entry point for the test script."""
    # Read the sample file
    sample_filename = "sample1.txt"
    print(f"Reading sample file: {sample_filename}")
    text = read_sample_file(sample_filename)
    print(f"Sample file contains {len(text)} characters and {len(text.split())} words.")
    print(f"First 100 characters: {text[:100]}")
    
    # Define the fields to extract
    fields = ["first_name", "last_name", "birthdate", "gender", "address", "phone", "medical_history"]
    print(f"Extracting fields: {', '.join(fields)}")
    
    # Use only the first 1000 words of the text
    text_sample = ' '.join(text.split()[:1000])
    print(f"Using a sample of {len(text_sample.split())} words.")
    
    # Test chunking directly
    from src.chunking.text_chunker import chunk_text
    chunks = chunk_text(text_sample, 100, 10)
    print(f"Direct chunking: {len(chunks)} chunks")
    
    # Print the first 10 words of the text
    print(f"First 10 words: {' '.join(text_sample.split()[:10])}")
    
    # Extract fields from the text
    result = extract_fields(text_sample, fields, chunk_size=100, chunk_overlap=10)
    
    # Display the results
    if result:
        print("\nExtracted Fields:")
        print("-" * 50)
        
        # Print the extracted fields
        extracted_fields = result.get("extracted_fields", {})
        for field, value in extracted_fields.items():
            if isinstance(value, list):
                print(f"{field}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{field}: {value}")
        
        # Print metrics
        print("\nMetrics:")
        print("-" * 50)
        metrics = result.get("metrics", {})
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        # Save the results to a file
        output_dir = "output_results"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"api_test_{sample_filename.split('.')[0]}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
