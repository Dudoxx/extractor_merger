"""
Formatters module for the DUDOXX field extraction system.
Provides functions for formatting output in different formats.
"""
import json
from src.config import settings

def format_output(data, output_format=None):
    """
    Format the output in the specified format.
    
    Args:
        data (dict): Data to format
        output_format (str, optional): Output format (json, text, md, csv, html). Defaults to settings.OUTPUT_FORMAT.
        
    Returns:
        str: Formatted output
    """
    # Use environment settings if not provided
    output_format = output_format or settings.OUTPUT_FORMAT
    
    # Format the output based on the specified format
    if output_format.lower() == 'json':
        return format_json(data)
    elif output_format.lower() == 'text':
        return format_text(data)
    elif output_format.lower() == 'md':
        return format_markdown(data)
    elif output_format.lower() == 'csv':
        return format_csv(data)
    elif output_format.lower() == 'html':
        return format_html(data)
    else:
        # Default to JSON
        return format_json(data)

def format_json(data):
    """
    Format the output as JSON.
    
    Args:
        data (dict): Data to format
        
    Returns:
        str: JSON-formatted output
    """
    return json.dumps(data, indent=2, ensure_ascii=False)

def format_text(data):
    """
    Format the output as plain text.
    
    Args:
        data (dict): Data to format
        
    Returns:
        str: Text-formatted output
    """
    lines = []
    
    for key, value in data.items():
        # Format list values
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    
    return '\n'.join(lines)

def format_markdown(data):
    """
    Format the output as Markdown.
    
    Args:
        data (dict): Data to format
        
    Returns:
        str: Markdown-formatted output
    """
    lines = ["# Extracted Fields", ""]
    
    for key, value in data.items():
        # Format list values
        if isinstance(value, list):
            lines.append(f"## {key}")
            for item in value:
                lines.append(f"- {item}")
            lines.append("")
        else:
            lines.append(f"**{key}**: {value}")
    
    return '\n'.join(lines)

def format_csv(data, fields=None):
    """
    Format the output as CSV.
    
    Args:
        data (dict): Data to format
        fields (list, optional): List of fields to include in the CSV. If None, all fields are included.
        
    Returns:
        str: CSV-formatted output
    """
    # Use all fields if not provided
    fields = fields or list(data.keys())
    
    # Create the header row
    header = ','.join(f'"{field}"' for field in fields)
    
    # Create the data row
    values = []
    for field in fields:
        value = data.get(field, '')
        
        # Format list values
        if isinstance(value, list):
            value = '; '.join(str(item) for item in value)
        
        # Escape quotes and wrap in quotes
        value = '"' + str(value).replace('"', '""') + '"'
        values.append(value)
    
    data_row = ','.join(values)
    
    # Combine header and data
    return f"{header}\n{data_row}"

def format_html(data):
    """
    Format the output as HTML.
    
    Args:
        data (dict): Data to format
        
    Returns:
        str: HTML-formatted output
    """
    lines = ['<!DOCTYPE html>', '<html>', '<head>', 
             '<meta charset="UTF-8">', 
             '<title>Extracted Fields</title>', 
             '<style>',
             'body { font-family: Arial, sans-serif; margin: 20px; }',
             'h1 { color: #333; }',
             'h2 { color: #666; margin-top: 20px; }',
             '.field { margin-bottom: 10px; }',
             '.field-name { font-weight: bold; }',
             '.field-value { margin-left: 10px; }',
             'ul { margin-top: 5px; }',
             '</style>',
             '</head>', 
             '<body>', 
             '<h1>Extracted Fields</h1>']
    
    for key, value in data.items():
        # Format list values
        if isinstance(value, list):
            lines.append(f'<h2>{key}</h2>')
            lines.append('<ul>')
            for item in value:
                lines.append(f'<li>{item}</li>')
            lines.append('</ul>')
        else:
            lines.append('<div class="field">')
            lines.append(f'<span class="field-name">{key}:</span>')
            lines.append(f'<span class="field-value">{value}</span>')
            lines.append('</div>')
    
    lines.extend(['</body>', '</html>'])
    
    return '\n'.join(lines)
