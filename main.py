#!/usr/bin/env python3
"""
Main entry point for the DUDOXX field extraction system.
"""
import os
import sys
import argparse
import time
from src.config import settings
from src.api.dudoxx_client import DudoxxClient
from src.chunking.text_chunker import chunk_text, chunk_text_by_paragraphs
from src.extraction.field_extractor import extract_fields_from_chunk
from src.processing.parallel_processor import process_chunks_parallel
from src.merging.result_merger import merge_results
from src.utils.formatters import format_output
from src.utils.validators import validate_and_normalize

def main():
    """Main entry point for the field extraction system."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Extract fields from long-form text using DUDOXX LLM.')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--fields', required=True, help='Comma-separated list of fields to extract')
    parser.add_argument('--output', help='Path to the output file (without extension)')
    parser.add_argument('--format', choices=['json', 'text', 'md', 'csv', 'html'], default=settings.OUTPUT_FORMAT, 
                        help='Output format')
    parser.add_argument('--chunk-method', choices=['words', 'paragraphs'], default='words',
                        help='Method for chunking text')
    parser.add_argument('--chunk-size', type=int, default=settings.CHUNK_SIZE,
                        help='Size of each chunk in words')
    parser.add_argument('--chunk-overlap', type=int, default=settings.CHUNK_OVERLAP,
                        help='Overlap between chunks in words')
    parser.add_argument('--max-threads', type=int, default=settings.MAX_THREADS,
                        help='Maximum number of worker threads')
    parser.add_argument('--date-fields', help='Comma-separated list of date fields to normalize')
    parser.add_argument('--date-format', default=settings.DATE_FORMAT,
                        help='Format for date fields')
    parser.add_argument('--unknown-value', default=settings.UNKNOWN_VALUE,
                        help='Value to use for unknown fields')
    parser.add_argument('--system-prompt', default=settings.DEFAULT_SYSTEM_PROMPT,
                        help='System prompt to use')
    
    args = parser.parse_args()
    
    # Parse fields
    fields = [field.strip() for field in args.fields.split(',')]
    
    # Parse date fields if provided
    date_fields = None
    if args.date_fields:
        date_fields = [field.strip() for field in args.date_fields.split(',')]
    
    # Ensure input_data directory exists
    os.makedirs('input_data', exist_ok=True)
    
    # Ensure output_results directory exists
    os.makedirs('output_results', exist_ok=True)
    
    # Determine input file path
    if os.path.isabs(args.input_file):
        input_path = args.input_file
    else:
        input_path = os.path.join('input_data', args.input_file)
    
    # Check if input file exists
    if not os.path.isfile(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)
    
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
    
    # Chunk the text
    print(f"Chunking text using {args.chunk_method} method...")
    start_time = time.time()
    if args.chunk_method == 'words':
        chunks = chunk_text(text, args.chunk_size, args.chunk_overlap)
    else:  # paragraphs
        chunks = chunk_text_by_paragraphs(text, args.chunk_size, args.chunk_overlap)
    
    print(f"Text chunked into {len(chunks)} chunks in {time.time() - start_time:.2f} seconds")
    
    # Define the processing function
    def process_chunk(chunk, chunk_idx):
        return extract_fields_from_chunk(
            chunk, 
            fields,
            chunk_index=chunk_idx,
            system_prompt=args.system_prompt,
            output_format=args.format,
            unknown_value=args.unknown_value,
            date_format=args.date_format
        )
    
    # Process chunks in parallel
    print(f"Processing chunks in parallel with {args.max_threads} threads...")
    start_time = time.time()
    chunk_results = process_chunks_parallel(chunks, process_chunk, args.max_threads)
    print(f"Chunks processed in {time.time() - start_time:.2f} seconds")
    
    # Merge results
    print("Merging results...")
    start_time = time.time()
    merged_results = merge_results(chunk_results, fields, args.unknown_value)
    
    # Validate and normalize results
    validated_results = validate_and_normalize(
        merged_results, 
        fields, 
        date_fields,
        args.unknown_value,
        args.date_format
    )
    print(f"Results merged and validated in {time.time() - start_time:.2f} seconds")
    
    # Format and save output
    output_format = args.format.lower()
    formatted_output = format_output(validated_results, output_format)
    
    # Save output in the specified format
    output_path = f"{output_base}.{output_format}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted_output)
    
    print(f"Extraction complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
