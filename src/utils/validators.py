"""
Validators module for the DUDOXX field extraction system.
Provides functions for validating and normalizing extracted data.
"""
import re
from datetime import datetime
from src.config import settings

def validate_fields(data, fields, unknown_value=None):
    """
    Validate extracted fields and ensure all required fields are present.
    
    Args:
        data (dict): Extracted data
        fields (list): List of field names to validate
        unknown_value (str, optional): Value to use for unknown fields. Defaults to settings.UNKNOWN_VALUE.
        
    Returns:
        dict: Validated data
    """
    # Use environment settings if not provided
    unknown_value = unknown_value or settings.UNKNOWN_VALUE
    
    # Ensure all required fields are present
    validated = {}
    for field in fields:
        if field in data:
            validated[field] = data[field]
        else:
            validated[field] = unknown_value
    
    return validated

def normalize_dates(data, date_fields=None, date_format=None):
    """
    Normalize date fields to the specified format.
    
    Args:
        data (dict): Extracted data
        date_fields (list, optional): List of date field names. If None, fields with 'date' in the name are normalized.
        date_format (str, optional): Format for date fields. Defaults to settings.DATE_FORMAT.
        
    Returns:
        dict: Data with normalized dates
    """
    # Use environment settings if not provided
    date_format = date_format or settings.DATE_FORMAT
    
    # If date_fields is not provided, use fields with 'date' in the name
    if date_fields is None:
        date_fields = [field for field in data.keys() if 'date' in field.lower()]
    
    # Normalize each date field
    normalized = data.copy()
    for field in date_fields:
        if field in normalized and normalized[field] != settings.UNKNOWN_VALUE:
            try:
                normalized[field] = normalize_date(normalized[field], date_format)
            except ValueError:
                # If normalization fails, keep the original value
                pass
    
    return normalized

def normalize_date(date_str, date_format=None):
    """
    Normalize a date string to the specified format.
    
    Args:
        date_str (str): Date string to normalize
        date_format (str, optional): Target date format. Defaults to settings.DATE_FORMAT.
        
    Returns:
        str: Normalized date string
    """
    # Use environment settings if not provided
    date_format = date_format or settings.DATE_FORMAT
    
    # Convert date_format to Python's strftime format
    py_format = date_format.replace('dd', '%d').replace('mm', '%m').replace('YYYY', '%Y')
    
    # Try to parse the date using various formats
    parsed_date = None
    
    # First, try to parse using common formats
    formats = [
        '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d',  # Common formats
        '%d-%m-%Y', '%m-%d-%Y',              # Dash formats
        '%d.%m.%Y', '%m.%d.%Y',              # Dot formats
        '%B %d, %Y', '%d %B %Y',             # Month name formats
        '%b %d, %Y', '%d %b %Y',             # Abbreviated month formats
        '%d %b, %Y', '%b %d %Y',             # Variations
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue
    
    # If that fails, try to extract day, month, year using regex
    if parsed_date is None:
        # Extract day, month, year using regex
        day_pattern = r'(\d{1,2})(?:st|nd|rd|th)?'
        month_pattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
        year_pattern = r'(\d{4}|\d{2})'
        
        # Try different patterns
        patterns = [
            # Day Month Year
            f"{day_pattern}\\s+{month_pattern}\\s+{year_pattern}",
            # Month Day Year
            f"{month_pattern}\\s+{day_pattern}\\s+{year_pattern}",
            # Year Month Day
            f"{year_pattern}\\s+{month_pattern}\\s+{day_pattern}",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                # Extract and convert to datetime
                # This is a simplified implementation
                # In a real-world scenario, you would need more sophisticated parsing
                pass
    
    # If parsing succeeded, format the date
    if parsed_date:
        return parsed_date.strftime(py_format)
    
    # If all parsing attempts fail, return the original string
    return date_str

def validate_and_normalize(data, fields=None, date_fields=None, unknown_value=None, date_format=None):
    """
    Validate and normalize extracted data.
    
    Args:
        data (dict): Extracted data
        fields (list, optional): List of field names to validate. If None, all fields in data are validated.
        date_fields (list, optional): List of date field names. If None, fields with 'date' in the name are normalized.
        unknown_value (str, optional): Value to use for unknown fields. Defaults to settings.UNKNOWN_VALUE.
        date_format (str, optional): Format for date fields. Defaults to settings.DATE_FORMAT.
        
    Returns:
        dict: Validated and normalized data
    """
    # Use environment settings if not provided
    unknown_value = unknown_value or settings.UNKNOWN_VALUE
    date_format = date_format or settings.DATE_FORMAT
    
    # If fields is not provided, use all fields in data
    fields = fields or list(data.keys())
    
    # Validate fields
    validated = validate_fields(data, fields, unknown_value)
    
    # Normalize dates
    normalized = normalize_dates(validated, date_fields, date_format)
    
    return normalized
