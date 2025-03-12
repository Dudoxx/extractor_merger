#!/usr/bin/env python3
"""
Test script for the DUDOXX Field Extractor API file upload functionality.
Uploads a sample text file to the API and displays the results.
"""
import os
import json
import time
import requests
from pprint import pprint

# API configuration
API_URL = "http://localhost:8000/api/v1/extract/file"
API_TOKEN = "sk-dudoxx-2025"  # From dudoxx-llm.env
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def extract_fields_from_file(file_path, fields, chunking_method="words", chunk_size=1000, chunk_overlap=100):
    """
    Extract fields from a file using the API.
    
    Args:
        file_path (str): Path to the file to extract fields from
        fields (list): List of fields to extract
        chunking_method (str, optional): Method for chunking text. Defaults to "words".
        chunk_size (int, optional): Size of each chunk in words. Defaults to 1000.
        chunk_overlap (int, optional): Overlap between chunks in words. Defaults to 100.
        
    Returns:
        dict: The API response
    """
    # Prepare the request payload
    payload = {
        "fields": ",".join(fields),
        "chunking_method": chunking_method,
        "chunk_size": str(chunk_size),
        "chunk_overlap": str(chunk_overlap),
        "max_workers": "5",
        "output_format": "json"
    }
    
    # Prepare the file
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "text/plain")
    }
    
    # Send the request to the API
    print(f"Sending file upload request to {API_URL}...")
    start_time = time.time()
    response = requests.post(API_URL, headers=HEADERS, data=payload, files=files)
    elapsed_time = time.time() - start_time
    
    # Close the file
    files["file"][1].close()
    
    # Check if the request was successful
    if response.status_code == 200:
        print(f"Request successful! Response received in {elapsed_time:.2f} seconds.")
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    """Main entry point for the test script."""
    # Define the file path
    file_path = "input_data/sample2.txt"
    print(f"Using file: {file_path}")
    
    # Get file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    
    # Define the fields to extract
    fields = ["first_name", "last_name", "birthdate", "gender", "address", "phone", "medical_history"]
    print(f"Extracting fields: {', '.join(fields)}")
    
    # Run 10 concurrent requests
    print(f"Running 10 concurrent requests...")
    import concurrent.futures
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit 10 requests
        futures = [executor.submit(extract_fields_from_file, file_path, fields, chunk_size=500, chunk_overlap=50) for _ in range(10)]
        
        # Process results as they complete
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                result = future.result()
                results.append(result)
                print(f"Request {i+1}/10 completed")
            except Exception as e:
                print(f"Request {i+1}/10 failed: {str(e)}")
    
    # Use the first successful result for display
    result = next((r for r in results if r), None)
    
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
        output_path = os.path.join(output_dir, f"api_test_file_upload_{os.path.basename(file_path).split('.')[0]}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()
