"""
Text chunking module for the DUDOXX field extraction system.
Provides functions for splitting long text into smaller chunks with overlap.
"""
from src.config import settings

def chunk_text(text, chunk_size=None, chunk_overlap=None, min_chunk_size=None):
    """
    Split text into chunks based on word count.
    
    Args:
        text (str): The input text to chunk
        chunk_size (int, optional): Size of each chunk in words. Defaults to settings.CHUNK_SIZE.
        chunk_overlap (int, optional): Overlap between chunks in words. Defaults to settings.CHUNK_OVERLAP.
        min_chunk_size (int, optional): Minimum chunk size. Defaults to settings.MIN_CHUNK_SIZE.
        
    Returns:
        list: List of text chunks
    """
    # Use environment settings if not provided
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    min_chunk_size = min_chunk_size or settings.MIN_CHUNK_SIZE
    
    # Implementation of chunking logic
    words = text.split()
    chunks = []
    
    # Handle case where text is shorter than chunk_size
    if len(words) <= chunk_size:
        return [text]
    
    # Create chunks with overlap
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk_words = words[i:i + chunk_size]
        
        # Skip chunks smaller than min_chunk_size unless it's the last chunk
        if len(chunk_words) < min_chunk_size and i + chunk_size < len(words):
            continue
            
        chunk = ' '.join(chunk_words)
        chunks.append(chunk)
    
    return chunks

def chunk_text_by_paragraphs(text, max_chunk_size=None, chunk_overlap=None, min_chunk_size=None):
    """
    Split text into chunks based on paragraphs, trying to keep paragraphs intact.
    
    Args:
        text (str): The input text to chunk
        max_chunk_size (int, optional): Maximum size of each chunk in words. Defaults to settings.CHUNK_SIZE.
        chunk_overlap (int, optional): Overlap between chunks in words. Defaults to settings.CHUNK_OVERLAP.
        min_chunk_size (int, optional): Minimum chunk size. Defaults to settings.MIN_CHUNK_SIZE.
        
    Returns:
        list: List of text chunks
    """
    # Use environment settings if not provided
    max_chunk_size = max_chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    min_chunk_size = min_chunk_size or settings.MIN_CHUNK_SIZE
    
    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Handle case where text is empty or has no paragraphs
    if not paragraphs:
        return []
    
    chunks = []
    current_chunk = []
    current_size = 0
    overlap_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph_size = len(paragraph.split())
        
        # If adding this paragraph would exceed max_chunk_size, finalize the current chunk
        if current_size + paragraph_size > max_chunk_size and current_size >= min_chunk_size:
            # Finalize current chunk
            chunks.append(' '.join(current_chunk))
            
            # Start a new chunk with overlap
            current_chunk = overlap_paragraphs.copy()
            current_size = sum(len(p.split()) for p in overlap_paragraphs)
            
            # Update overlap paragraphs
            overlap_paragraphs = []
        
        # Add paragraph to current chunk
        current_chunk.append(paragraph)
        current_size += paragraph_size
        
        # Update overlap paragraphs (keep track of recent paragraphs for overlap)
        overlap_paragraphs.append(paragraph)
        overlap_size = sum(len(p.split()) for p in overlap_paragraphs)
        
        # Trim overlap if it gets too large
        while overlap_size > chunk_overlap and len(overlap_paragraphs) > 1:
            removed = overlap_paragraphs.pop(0)
            overlap_size -= len(removed.split())
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks
