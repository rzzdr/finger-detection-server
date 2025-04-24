"""
Compatibility utilities to handle differences between Pydantic v1 and v2.
"""

def ensure_pydantic_compatibility():
    """
    Ensure compatibility with Pydantic v2 by patching necessary features.
    """
    try:
        # Check if we're using Pydantic v2
        import pydantic
        v2 = int(pydantic.__version__.split('.')[0]) >= 2
        
        if v2:
            # Configure Pydantic v2 to be more compatible with FastAPI expectations
            from pydantic import ConfigDict
            import pydantic.json_schema
            
            # Add compatibility patches if needed here
            
    except (ImportError, AttributeError):
        # If any import fails, we can't determine the version or apply patches
        pass
