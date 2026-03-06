import os
from rembg import new_session
from pathlib import Path

def download_model():
    """
    Forces the download of the u2net model by initializing a session.
    This is used during Docker build to bake the model into the image.
    """
    print("Pre-downloading AI model (u2net)...")
    # This will trigger the download if not present
    new_session("u2net")
    
    # Verify it exists in the default location
    model_path = Path.home() / ".u2net" / "u2net.onnx"
    if model_path.exists():
        print(f"Model successfully downloaded to {model_path}")
        print(f"Size: {model_path.stat().st_size / (1024*1024):.2f} MB")
    else:
        print("Warning: Model path not found at expected location.")

if __name__ == "__main__":
    download_model()
