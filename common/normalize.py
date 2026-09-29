import re

def normalize_url(text):
    """
    Normalizes a URL by:
    - Lowercasing
    - Stripping whitespace
    - Removing leading http:// or https://
    - Removing a leading www.
    - Removing a trailing /
    """
    if not isinstance(text, str):
        return str(text)
        
    text = text.lower().strip()
    
    # Remove http:// or https://
    text = re.sub(r'^https?://', '', text)
    
    # Remove www.
    if text.startswith('www.'):
        text = text[4:]
        
    # Remove trailing /
    if text.endswith('/'):
        text = text[:-1]
        
    return text
