"""
Parallel processing module for the DUDOXX field extraction system.
Provides functions for processing chunks in parallel using ThreadPoolExecutor.
"""
import concurrent.futures
import time
from src.config import settings

def process_chunks_parallel(chunks, process_func, max_workers=None, batch_size=None):
    """
    Process chunks in parallel using ThreadPoolExecutor.
    
    Args:
        chunks (list): List of text chunks to process
        process_func (callable): Function to process each chunk
        max_workers (int, optional): Maximum number of worker threads. Defaults to settings.MAX_THREADS.
        batch_size (int, optional): Number of chunks to process in each batch. Defaults to settings.BATCH_SIZE.
        
    Returns:
        list: List of results from processing each chunk
    """
    # Use environment settings if not provided
    max_workers = max_workers or settings.MAX_THREADS
    batch_size = batch_size or settings.BATCH_SIZE
    
    results = []
    
    # Process chunks in batches to avoid overwhelming the API
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_results = []
        
        print(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size} "
              f"({len(batch)} chunks)...")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers, len(batch))) as executor:
            # Submit all tasks
            future_to_chunk = {executor.submit(process_func, chunk, idx): idx 
                              for idx, chunk in enumerate(batch)}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk_idx = future_to_chunk[future]
                try:
                    result = future.result()
                    batch_results.append((chunk_idx, result))
                except Exception as e:
                    print(f"Error processing chunk {chunk_idx}: {str(e)}")
                    batch_results.append((chunk_idx, None))
        
        # Sort results by original chunk index
        batch_results.sort(key=lambda x: x[0])
        results.extend([r[1] for r in batch_results])
        
        elapsed = time.time() - start_time
        print(f"Batch processed in {elapsed:.2f} seconds")
    
    return results

def process_with_timeout(func, args=(), kwargs=None, timeout=None):
    """
    Execute a function with a timeout.
    
    Args:
        func (callable): Function to execute
        args (tuple): Positional arguments for the function
        kwargs (dict, optional): Keyword arguments for the function
        timeout (int, optional): Timeout in seconds. Defaults to settings.REQUEST_TIMEOUT.
        
    Returns:
        Any: Result of the function or None if timeout occurs
    """
    if kwargs is None:
        kwargs = {}
    
    timeout = timeout or settings.REQUEST_TIMEOUT
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"Function execution timed out after {timeout} seconds")
            return None
