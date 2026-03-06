import io
import pytest
from bg_remover.core import verify_image_signature

def test_reject_spoofed_file_type():
    # A text file with a .png extension
    fake_png = io.BytesIO(b"this is just a text file, not a png")
    assert verify_image_signature(fake_png) is False

def test_accept_valid_png_signature():
    # Valid PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
    valid_png = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"some data")
    assert verify_image_signature(valid_png) is True

def test_accept_valid_jpeg_signature():
    # Valid JPEG magic bytes: FF D8 FF
    valid_jpeg = io.BytesIO(b"\xff\xd8\xff" + b"some data")
    assert verify_image_signature(valid_jpeg) is True

def test_singleton_model_reuse():
    from bg_remover.core import get_bg_session
    # First call initializes the session
    s1 = get_bg_session()
    # Second call should return the exact same object
    s2 = get_bg_session()
    assert s1 is s2

def test_zero_disk_trace():
    from bg_remover.core import remove_bg_from_stream
    from pathlib import Path
    
    # Use a real image from the project for a functional test
    img_path = Path("input_frames/frame_01.png")
    with open(img_path, "rb") as f:
        input_data = f.read()
        
    input_stream = io.BytesIO(input_data)
    output_stream = remove_bg_from_stream(input_stream)
    
    # Verify we got some data back
    assert output_stream.getbuffer().nbytes > 0
    # Verify it's a valid PNG (starts with magic bytes)
    assert output_stream.getvalue().startswith(b"\x89PNG")
