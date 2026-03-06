import io
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

# Absolute import from the package
from bg_remover.api.routes import app

client = TestClient(app)

def test_api_standard_workflow():
    img_path = Path("input_frames/frame_01.png")
    with open(img_path, "rb") as f:
        files = {"file": ("frame_01.png", f, "image/png")}
        response = client.post("/remove", files=files)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    # Verify magic bytes of the response content
    assert response.content.startswith(b"\x89PNG")

def test_api_rejects_non_image():
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/remove", files=files)
    assert response.status_code == 400
    assert "Invalid image" in response.json()["detail"]

def test_api_rejects_large_file():
    from bg_remover.core import MAX_FILE_SIZE_BYTES
    # Create a large dummy content
    large_content = b"a" * (MAX_FILE_SIZE_BYTES + 1)
    response = client.post(
        "/remove", 
        files={"file": ("large.png", large_content, "image/png")}
    )
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_key_auth_enforced(monkeypatch):
    # Set the API_KEY environment variable
    monkeypatch.setenv("BG_REMOVER_API_KEY", "secret-test-key")
    
    # Request without key should fail
    response = client.post("/remove", files={"file": ("test.png", b"\x89PNG\r\n\x1a\n", "image/png")})
    assert response.status_code == 401
    
    # Request with wrong key should fail
    response = client.post(
        "/remove", 
        files={"file": ("test.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        headers={"X-API-KEY": "wrong-key"}
    )
    assert response.status_code == 401

    # Request with correct key should pass
    response = client.post(
        "/remove", 
        files={"file": ("test.png", b"\x89PNG\r\n\x1a\n", "image/png")},
        headers={"X-API-KEY": "secret-test-key"}
    )
    # 400 is fine here as dummy data won't pass Pillow validation, but it passed Auth
    assert response.status_code in [200, 400]

def test_rate_limiting():
    # Hit the health endpoint rapidly
    for _ in range(15):
        response = client.get("/health")
        if response.status_code == 429:
            break
    
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["error"]

def test_error_confidentiality(monkeypatch):
    # Force an unexpected error in the route's imported function
    import bg_remover.api.routes
    def mock_remove_bg(*args, **kwargs):
        raise RuntimeError("Secret internal path: /home/andrei/source/bg_remover")
    
    monkeypatch.setattr(bg_remover.api.routes, "remove_bg_from_stream", mock_remove_bg)
    
    # Send a valid-looking request
    response = client.post(
        "/remove", 
        files={"file": ("test.png", b"\x89PNG\r\n\x1a\n", "image/png")}
    )
    
    assert response.status_code == 500
    assert "/home/andrei" not in response.text
    assert "RuntimeError" not in response.text
    assert "Internal server error" in response.json()["detail"]
