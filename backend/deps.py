import uuid

def generate_request_id() -> str:
    """
    Generates a unique request ID for tracking purposes.

    Returns:
        str: A unique request ID.
    
    """
    return str(uuid.uuid4())
