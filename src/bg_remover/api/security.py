import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

# API Key Security
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    # Load key from environment
    expected_key = os.getenv("BG_REMOVER_API_KEY")
    
    # If no key is configured in environment, allow all (public mode)
    if not expected_key:
        return None
        
    if api_key == expected_key:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
