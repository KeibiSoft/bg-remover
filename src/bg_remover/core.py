import io
import logging
import threading
from typing import Optional

from PIL import Image
from rembg import remove, new_session

# --- SECURITY & CONFIGURATION CONSTANTS ---
# Prevent Decompression Bombs (DoS attacks via massive images)
Image.MAX_IMAGE_PIXELS = 89_478_485  # Approx. 90 megapixels limit

# Limit maximum file size (e.g., 20 MB) to prevent memory exhaustion
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024

# Allowed output formats
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

# Shared AI session (Singleton)
_SESSION_LOCK = threading.Lock()
_SESSION_INSTANCE: Optional[any] = None

def get_bg_session():
    """Returns a singleton rembg session for reuse across requests."""
    global _SESSION_INSTANCE
    with _SESSION_LOCK:
        if _SESSION_INSTANCE is None:
            # Default model is 'u2net'
            _SESSION_INSTANCE = new_session()
    return _SESSION_INSTANCE

def verify_image_signature(file_stream: io.BytesIO) -> bool:
    """
    Verifies the 'magic bytes' of an image to prevent file spoofing.
    Supports PNG and JPEG.
    """
    # Peek at the first 8 bytes
    original_pos = file_stream.tell()
    header = file_stream.read(8)
    file_stream.seek(original_pos) # Reset position

    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    
    # JPEG: FF D8 FF
    if header.startswith(b"\xff\xd8\xff"):
        return True
        
    return False

def remove_bg_from_stream(input_stream: io.BytesIO) -> io.BytesIO:
    """
    Processes an image from a stream and returns a transparent PNG stream.
    Strictly in-memory (RAM-only).
    """
    session = get_bg_session()
    
    # Load image from stream
    input_image = Image.open(input_stream)
    
    # Perform background removal
    output_image = remove(input_image, session=session)
    
    # Save to memory stream as PNG
    output_stream = io.BytesIO()
    output_image.save(output_stream, format="PNG")
    output_stream.seek(0)
    
    return output_stream
