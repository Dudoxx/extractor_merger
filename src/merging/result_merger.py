"""
Result merger module for the DUDOXX field extraction system.
Provides functions for merging results from multiple chunks.
"""
import json
from src.config import settings
from src.api.dudoxx_client import DudoxxClient

# Initialize the DUDOXX client
dudoxx_client = DudoxxClient()

def merge_results(chunk_results, fields, unknown_value=None):
    """
    Merge results from multiple chunks into a single result.
    
    Args:
        chunk_results (list): List of results from processing each chunk
        fields (list): List of field names to extract
        unknown_value (str, optional): Value to use for unknown fields. Defaults to settings.UNKNOWN_VALUE.
        
    Returns:
        dict: Merged results
    """
    # Use environment settings if not provided
    unknown_value = unknown_value or settings.UNKNOWN_VALUE
    
    # Initialize merged results with unknown values
    merged = {field: unknown_value for field in fields}
    
    # Track fields that are lists (e.g., medical_history, education_history)
    list_fields = {}
    
    # Process each chunk result
    for result in chunk_results:
        if not result:
            continue
        
        # Handle error in result
        if isinstance(result, dict) and 'error' in result:
            print(f"Warning: Error in chunk result: {result['error']}")
            continue
        
        # Process each field
        for field in fields:
            # Skip if field is not in result
            if field not in result:
                continue
            
            # Get the value from the result
            value = result[field]
            
            # Skip unknown values
            if value == unknown_value:
                continue
            
            # If the merged value is unknown, use the value from this chunk
            if merged[field] == unknown_value:
                merged[field] = value
                continue
            
            # If the values are the same, continue
            if merged[field] == value:
                continue
            
            # If the values are different, we need to merge them
            # This could be a list field or a conflict
            
            # Check if this is a list field
            if isinstance(value, list) or isinstance(merged[field], list):
                # Convert to list if not already
                if not isinstance(merged[field], list):
                    merged[field] = [merged[field]]
                if not isinstance(value, list):
                    value = [value]
                
                # Merge the lists
                merged[field].extend(value)
                
                # Mark as a list field
                list_fields[field] = True
                
            elif field in list_fields or _is_list_field(field):
                # This is a list field, but the values are not lists
                # Convert to list and merge
                if not isinstance(merged[field], list):
                    merged[field] = [merged[field]]
                
                # Add the value if it's not already in the list
                if value not in merged[field]:
                    merged[field].append(value)
                
                # Mark as a list field
                list_fields[field] = True
                
            else:
                # This is a conflict between different values for the same field
                # We need a more sophisticated conflict resolution strategy
                
                # Strategy 1: Keep the longer value (more information)
                # This is a simple heuristic that works in many cases
                if len(str(value)) > len(str(merged[field])):
                    merged[field] = value
                    continue
                
                # Strategy 2: Check if one value is a substring of the other
                # If so, keep the more complete value
                if str(value) in str(merged[field]):
                    # Keep merged value as it's more complete
                    continue
                elif str(merged[field]) in str(value):
                    # Use the new value as it's more complete
                    merged[field] = value
                    continue
                
                # Strategy 3: For fields that might have formatting differences
                # (like phone numbers, addresses), normalize and compare
                normalized_value = _normalize_field(value, field)
                normalized_merged = _normalize_field(merged[field], field)
                
                if normalized_value == normalized_merged:
                    # Same content with different formatting, keep the better formatted one
                    if _format_quality_score(value, field) > _format_quality_score(merged[field], field):
                        merged[field] = value
                    continue
                
                # Strategy 4: If we still have a conflict, log it and keep the first value
                # This could be improved by asking the LLM to resolve the conflict
                print(f"Warning: Conflicting values for field '{field}': '{merged[field]}' vs '{value}'. Keeping first value.")
    
    # Post-process list fields
    for field in list_fields:
        if field in merged and isinstance(merged[field], list):
            # Use LLM-based deduplication for list fields
            merged[field] = deduplicate_with_llm(merged[field], field)
    
    return merged

def deduplicate_with_llm(items, field_name):
    """
    Use the DUDOXX LLM to deduplicate a list of items for a specific field.
    
    Args:
        items (list): List of items to deduplicate
        field_name (str): Name of the field (e.g., 'medical_history')
        
    Returns:
        list: Deduplicated list of items
    """
    if not items:
        return []
    
    # If there's only one item, no need to deduplicate
    if len(items) == 1:
        return items
    
    # Simple deduplication for common cases
    # This helps avoid unnecessary LLM calls for simple cases
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    
    # If we've reduced to a single item, return it
    if len(unique_items) == 1:
        return unique_items
    
    print(f"Deduplicating {field_name} items with LLM: {unique_items}")
    
    # Build the system prompt
    system_prompt = f"""You are an expert data deduplication assistant. Your task is to deduplicate a list of {field_name} items.
Some items may refer to the same information but with different wording, formatting, or level of detail.
Identify duplicate or similar items and merge them into a single, comprehensive item.
Always prefer the more detailed, complete, and well-formatted version when merging duplicates.

IMPORTANT: You must return ONLY a JSON array of strings, with no additional explanation, preamble, or conclusion.
Do not invent or hallucinate any information not present in the input data.
"""
    
    # Build the user prompt with examples
    user_prompt = f"""Here is a list of {field_name} items that may contain duplicates:

{json.dumps(items, indent=2)}

Please deduplicate this list by:
1. Identifying items that refer to the same information
2. Merging similar items into a single, comprehensive item
3. Keeping the most detailed, complete, and well-formatted version

EXPECTED OUTPUT FORMAT:
Return ONLY a JSON array of strings like this example:
["Item 1", "Item 2", "Item 3"]

For example, if the input is:
["Type 2 Diabetes (diagnosed March 15, 2010)", "Diagnosed with Type 2 Diabetes (March 15, 2010)", "Hypertension since 2005", "High blood pressure (Hypertension) since 2005"]

Your response should be:
["Type 2 Diabetes (diagnosed March 15, 2010)", "Hypertension since 2005"]

DO NOT include any explanations, notes, or additional information in your response.
DO NOT structure your response as an object with keys.
ONLY return a flat array of strings.
"""
    
    # Call the DUDOXX LLM API
    try:
        response = dudoxx_client.extract_fields(
            text=user_prompt,
            fields=["deduplicated_items"],
            system_prompt=system_prompt
        )
        
        # Parse the response
        if "deduplicated_items" in response:
            deduplicated_items = response["deduplicated_items"]
            
            # Ensure the result is a list
            if not isinstance(deduplicated_items, list):
                print(f"Warning: LLM deduplication returned non-list result: {deduplicated_items}")
                # Fall back to simple deduplication
                seen = set()
                return [x for x in items if not (x in seen or seen.add(x))]
            
            print(f"LLM deduplicated {len(items)} items to {len(deduplicated_items)} items")
            return deduplicated_items
        else:
            # The LLM might have returned a different format, try to extract useful information
            print(f"LLM returned a different format: {response}")
            
            # Check if the response contains a 'deduplicated_items' key in a nested structure
            if isinstance(response, list) and len(response) > 0 and isinstance(response[0], dict) and 'deduplicated_items' in response[0]:
                # Extract the deduplicated_items from the nested structure
                nested_items = response[0]['deduplicated_items']
                if isinstance(nested_items, list):
                    # Convert structured format to strings
                    deduplicated_items = []
                    for item in nested_items:
                        # Format depends on the field
                        if field_name == "medical_history":
                            # Format medical history items
                            # Look for condition fields with various names
                            condition = ""
                            condition_fields = ["medical_condition", "condition", "diagnosis", "procedure", "treatment", "event"]
                            for condition_field in condition_fields:
                                if condition_field in item and item[condition_field]:
                                    condition = item[condition_field]
                                    break
                            
                            # Look for date fields with various names
                            date = ""
                            date_fields = [
                                "date", "date_diagnosed", "date_started", "date_performed", "year",
                                "date_of_diagnosis", "start_date", "date_of_procedure", "when",
                                "date_procedure", "date_surgery", "date_event", "date_treatment",
                                "diagnosed_on", "performed_on", "started_on", "occurred_on"
                            ]
                            for date_field in date_fields:
                                if date_field in item and item[date_field] and item[date_field].lower() != "unknown":
                                    date = item[date_field]
                                    break
                            
                            # Format the item
                            if condition and date:
                                formatted_item = f"{condition} ({date})"
                            else:
                                formatted_item = condition
                            
                            deduplicated_items.append(formatted_item)
                        else:
                            # For other fields, just convert the dict to a string
                            deduplicated_items.append(str(item))
                    
                    print(f"Converted nested deduplicated_items to {len(deduplicated_items)} items")
                    return deduplicated_items
            
            # Check if the response is a list of dictionaries (structured format)
            elif isinstance(response, list) and all(isinstance(item, dict) for item in response):
                # Convert structured format to strings
                deduplicated_items = []
                for item in response:
                    # Format depends on the field
                    if field_name == "medical_history":
                        # Format medical history items
                        # Look for condition fields with various names
                        condition = ""
                        condition_fields = ["medical_condition", "condition", "diagnosis", "procedure", "treatment", "event"]
                        for condition_field in condition_fields:
                            if condition_field in item and item[condition_field]:
                                condition = item[condition_field]
                                break
                        
                        # Look for date fields with various names
                        date = ""
                        date_fields = [
                            "date", "date_diagnosed", "date_started", "date_performed", "year",
                            "date_of_diagnosis", "start_date", "date_of_procedure", "when",
                            "date_procedure", "date_surgery", "date_event", "date_treatment",
                            "diagnosed_on", "performed_on", "started_on", "occurred_on"
                        ]
                        for date_field in date_fields:
                            if date_field in item and item[date_field]:
                                date = item[date_field]
                                break
                        
                        # Format the item
                        if condition and date and date.lower() != "unknown":
                            formatted_item = f"{condition} ({date})"
                        else:
                            formatted_item = condition
                        
                        deduplicated_items.append(formatted_item)
                    else:
                        # For other fields, just convert the dict to a string
                        deduplicated_items.append(str(item))
                
                print(f"Converted structured response to {len(deduplicated_items)} items")
                return deduplicated_items
            
            # Check if the response is a list of strings (direct format)
            if isinstance(response, list) and all(isinstance(item, str) for item in response):
                print(f"LLM returned a list of {len(response)} strings")
                return response
            
            # Fall back to simple deduplication
            print(f"Warning: LLM deduplication failed to return deduplicated_items: {response}")
            seen = set()
            return [x for x in items if not (x in seen or seen.add(x))]
    
    except Exception as e:
        print(f"Error in LLM deduplication: {str(e)}")
        # Fall back to simple deduplication
        seen = set()
        return [x for x in items if not (x in seen or seen.add(x))]

def _is_list_field(field):
    """
    Check if a field is likely to be a list field based on its name.
    
    Args:
        field (str): Field name
        
    Returns:
        bool: True if the field is likely to be a list field, False otherwise
    """
    list_indicators = [
        'history', 'histories', 'list', 'lists', 'items', 'entries',
        'events', 'experiences', 'education', 'work', 'jobs', 'skills',
        'qualifications', 'certifications', 'publications', 'awards',
        'achievements', 'projects', 'responsibilities', 'duties',
        'medications', 'conditions', 'symptoms', 'diagnoses', 'treatments',
        'procedures', 'allergies', 'immunizations', 'vaccinations',
        'addresses', 'phones', 'emails', 'contacts', 'references',
        'hobbies', 'interests', 'languages', 'memberships', 'affiliations'
    ]
    
    # Check if the field name contains any list indicators
    return any(indicator in field.lower() for indicator in list_indicators)

def merge_date_fields(chunk_results, date_fields, unknown_value=None, date_format=None):
    """
    Merge date fields from multiple chunks, ensuring consistent formatting.
    
    Args:
        chunk_results (list): List of results from processing each chunk
        date_fields (list): List of date field names
        unknown_value (str, optional): Value to use for unknown fields. Defaults to settings.UNKNOWN_VALUE.
        date_format (str, optional): Format for date fields. Defaults to settings.DATE_FORMAT.
        
    Returns:
        dict: Merged date fields
    """
    # Use environment settings if not provided
    unknown_value = unknown_value or settings.UNKNOWN_VALUE
    date_format = date_format or settings.DATE_FORMAT
    
    # Initialize merged results with unknown values
    merged = {field: unknown_value for field in date_fields}
    
    # Process each chunk result
    for result in chunk_results:
        if not result:
            continue
        
        # Process each date field
        for field in date_fields:
            # Skip if field is not in result
            if field not in result:
                continue
            
            # Get the value from the result
            value = result[field]
            
            # Skip unknown values
            if value == unknown_value:
                continue
            
            # If the merged value is unknown, use the value from this chunk
            if merged[field] == unknown_value:
                merged[field] = _normalize_date(value, date_format)
                continue
            
            # If the values are the same, continue
            if merged[field] == value:
                continue
            
            # If the values are different, normalize and compare
            normalized_value = _normalize_date(value, date_format)
            normalized_merged = _normalize_date(merged[field], date_format)
            
            # If the normalized values are the same, keep the better formatted one
            if normalized_value == normalized_merged:
                # Keep the one that matches the date format better
                if _date_format_score(value, date_format) > _date_format_score(merged[field], date_format):
                    merged[field] = value
            else:
                # Different dates, keep the more complete one
                # This could be improved with more sophisticated conflict resolution
                if _date_completeness_score(value) > _date_completeness_score(merged[field]):
                    merged[field] = normalized_value
    
    return merged

def _normalize_date(date_str, date_format):
    """
    Normalize a date string to the specified format.
    
    Args:
        date_str (str): Date string to normalize
        date_format (str): Target date format
        
    Returns:
        str: Normalized date string
    """
    # This is a simplified implementation
    # In a real-world scenario, you would use a date parsing library
    # For now, we'll just return the original string
    return date_str

def _date_format_score(date_str, date_format):
    """
    Calculate a score for how well a date string matches the specified format.
    
    Args:
        date_str (str): Date string to score
        date_format (str): Target date format
        
    Returns:
        int: Score (higher is better)
    """
    # This is a simplified implementation
    # In a real-world scenario, you would use a date parsing library
    # For now, we'll just return a simple score
    score = 0
    
    # Check if the date string contains slashes
    if '/' in date_str:
        score += 1
    
    # Check if the date string has the right length
    if len(date_str) == len('dd/mm/YYYY'):
        score += 1
    
    return score

def _date_completeness_score(date_str):
    """
    Calculate a score for how complete a date string is.
    
    Args:
        date_str (str): Date string to score
        
    Returns:
        int: Score (higher is better)
    """
    # This is a simplified implementation
    # In a real-world scenario, you would use a date parsing library
    # For now, we'll just return a simple score
    score = 0
    
    # Check if the date string contains day, month, and year
    parts = date_str.replace('/', '-').replace('.', '-').split('-')
    score += len(parts)
    
    # Check if the date string has a 4-digit year
    for part in parts:
        if len(part) == 4 and part.isdigit():
            score += 1
    
    return score

def _normalize_field(value, field):
    """
    Normalize a field value for comparison.
    
    Args:
        value: The field value to normalize
        field (str): The field name
        
    Returns:
        str: Normalized field value
    """
    # Convert to string
    value_str = str(value)
    
    # Normalize based on field type
    if 'phone' in field.lower():
        # Remove non-digit characters for phone numbers
        return ''.join(c for c in value_str if c.isdigit())
    
    elif 'email' in field.lower():
        # Lowercase emails
        return value_str.lower()
    
    elif 'address' in field.lower():
        # Normalize addresses: lowercase, remove extra spaces, standardize separators
        normalized = value_str.lower()
        normalized = ' '.join(normalized.split())  # Remove extra spaces
        normalized = normalized.replace(',', ' ').replace('.', ' ')
        normalized = ' '.join(normalized.split())  # Remove extra spaces again
        return normalized
    
    elif 'name' in field.lower():
        # Normalize names: lowercase, remove extra spaces
        normalized = value_str.lower()
        normalized = ' '.join(normalized.split())
        return normalized
    
    # Default normalization: lowercase and remove extra spaces
    return ' '.join(value_str.lower().split())

def _format_quality_score(value, field):
    """
    Calculate a score for the formatting quality of a field value.
    
    Args:
        value: The field value to score
        field (str): The field name
        
    Returns:
        int: Score (higher is better)
    """
    value_str = str(value)
    score = 0
    
    # Score based on field type
    if 'phone' in field.lower():
        # Phone numbers with proper formatting (parentheses, dashes, etc.)
        if '(' in value_str and ')' in value_str:
            score += 1
        if '-' in value_str:
            score += 1
    
    elif 'email' in field.lower():
        # Email with proper domain
        if '@' in value_str and '.' in value_str.split('@')[-1]:
            score += 2
    
    elif 'address' in field.lower():
        # Address with proper formatting (commas, proper case)
        if ',' in value_str:
            score += 1
        if any(c.isupper() for c in value_str):
            score += 1
    
    elif 'name' in field.lower():
        # Names with proper capitalization
        words = value_str.split()
        if all(word[0].isupper() for word in words if word):
            score += 2
    
    # General formatting quality
    # Prefer values with proper capitalization
    if any(c.isupper() for c in value_str):
        score += 1
    
    # Prefer values with proper punctuation
    if any(c in value_str for c in ',.;:'):
        score += 1
    
    return score
