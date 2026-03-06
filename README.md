# ✂️ AI Background Remover (Secure AI Artifact)

[![Maintained by KeibiSoft](https://img.shields.io/badge/Maintained%20by-KeibiSoft-blue?style=for-the-badge)](https://keibisoft.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Security: Hardened](https://img.shields.io/badge/Security-Hardened-success?style=for-the-badge)](#🛡️-security-audit)

A production-ready CLI tool and REST API built with Python to batch-remove backgrounds from images using local AI models. 

**This repository is a KeibiSoft Security Artifact.** It serves as a reference implementation for secure, local-first AI services, demonstrating how to integrate high-performance inference with strict SSDLC standards.

Unlike cloud-based alternatives, this tool runs **entirely on your machine**. No data is uploaded to third-party servers, ensuring absolute privacy and data sovereignty.

## ✨ Key Features

*   **Dual-Mode Operation**: Use it as a one-off **CLI tool** for batch processing or a persistent **REST API** service.
*   **100% Local Processing**: Privacy-first approach; works offline after the initial model download.
*   **Hardware Flexible**: Optimized for both CPU-only systems and NVIDIA GPU acceleration.
*   **Security Hardened**: 
    *   **Path Traversal Protection**: Prevents unauthorized file access.
    *   **DoS Protection**: Enforces strict pixel, file size, and rate limits.
    *   **Magic Byte Validation**: Verifies file integrity (PNG/JPEG) before processing.
*   **Docker Ready**: Includes a hardened, non-root, multi-stage Docker configuration.

## 🚀 Installation

This project requires **Python 3.12+** and is optimized for [uv](https://github.com/astral-sh/uv).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ac999/bg-remover
    cd bg-remover
    ```

2.  **Initialize the environment:**
    ```bash
    # For CPU usage
    uv sync --extra cpu
    
    # For NVIDIA GPU (Requires CUDA)
    uv sync --extra gpu
    
    # For API Server + Testing
    uv sync --extra server --extra test --extra cpu
    ```

## 📖 Usage

### CLI Mode (Batch Processing)
Place your images in a folder (default: `input_frames`) and run:
```bash
uv run bg-remover cli
```

**Options:**
*   `-i, --input`: Input directory.
*   `-o, --output`: Output directory.
*   `-v, --verbose`: Enable debug logs.

### Server Mode (REST API)
Start the high-performance FastAPI server:
```bash
uv run bg-remover server
```
The API will be available at `http://localhost:8000`. View automatic documentation at `/docs`.

**Security Configuration:**
Copy `.env.example` to `.env` and set `BG_REMOVER_API_KEY` to secure your endpoint.

## 🐳 Docker Deployment

The fastest way to deploy the service on a VPS:
```bash
docker-compose up -d
```
The Docker image is hardened with a read-only root filesystem and restricted kernel capabilities.

## 🧪 Testing

This project follows a Test-Driven Development (TDD) approach.
```bash
uv run pytest
```

## 🛡️ Security Audit

*   **Resource Limits**: `MAX_IMAGE_PIXELS` and `MAX_FILE_SIZE_BYTES` are strictly enforced.
*   **API Security**: Built-in IP-based rate limiting and optional API Key authentication.
*   **Privacy**: API mode processes images strictly in-memory (`BytesIO`); no files are written to the server's disk.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
