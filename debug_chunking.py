#!/usr/bin/env python3
"""
Debug script for the chunking function.
"""
import sys
from src.chunking.text_chunker import chunk_text

def main():
    """Main entry point for the debug script."""
    # Create a test text
    text = ' '.join(['word'] * 1000)
    
    # Test chunking with different chunk sizes
    for chunk_size in [100, 200, 500, 1000]:
        chunks = chunk_text(text, chunk_size, 10)
        print(f"Chunk size: {chunk_size}, Number of chunks: {len(chunks)}")
    
    # Test with a real text
    with open('input_data/sample1.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Use only the first 1000 words
    text_sample = ' '.join(text.split()[:1000])
    
    # Test chunking with different chunk sizes
    for chunk_size in [100, 200, 500, 1000]:
        chunks = chunk_text(text_sample, chunk_size, 10)
        print(f"Sample text, Chunk size: {chunk_size}, Number of chunks: {len(chunks)}")

if __name__ == "__main__":
    main()
