import io
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Response, Depends, Request
from bg_remover.core import (
    remove_bg_from_stream, 
    verify_image_signature, 
    get_bg_session,
    MAX_FILE_SIZE_BYTES
)
from PIL import UnidentifiedImageError
from bg_remover.api.security import get_api_key, limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load the AI model on startup
    get_bg_session()
    yield

app = FastAPI(
    title="AI Background Remover API",
    description="Secure local AI service for background removal.",
    lifespan=lifespan
)

# Add Rate Limiting State & Error Handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {"status": "ok", "model": "u2net"}

@app.post("/remove")
@limiter.limit("5/minute")
async def remove_background(
    request: Request,
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    # Security: Check Content-Length header if available
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large.")

    # Read file into memory
    content = await file.read()
    
    # Double check actual size in memory
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large.")
        
    input_stream = io.BytesIO(content)
    
    # Security: Verify magic bytes
    if not verify_image_signature(input_stream):
        raise HTTPException(status_code=400, detail="Invalid image format. Supported: PNG, JPEG.")
    
    try:
        # Perform background removal
        output_stream = remove_bg_from_stream(input_stream)
        
        # Return as streaming response
        return Response(
            content=output_stream.getvalue(),
            media_type="image/png"
        )
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
    except Exception as e:
        # Generic error message for security (masking internal details)
        raise HTTPException(status_code=500, detail="Internal server error during processing.")
