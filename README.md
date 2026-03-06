# ✂️ AI Background Remover (Local & Secure)

A production-ready CLI tool built with Python to batch-remove backgrounds from images using local AI models. Designed for privacy, speed, and security.

Unlike cloud-based alternatives, this tool runs **entirely on your machine**. No data is uploaded to third-party servers, ensuring your images remain private and secure.

## ✨ Key Features

* **100% Local Processing**: Privacy-first approach; works offline after the initial model download.
* **Hardware Flexible**: Optimized for both CPU-only systems (Laptops/Macs) and NVIDIA GPU acceleration.
* **Security Hardened**: 
    * **Path Traversal Protection**: Prevents unauthorized file access outside designated folders.
    * **DoS Protection**: Enforces strict pixel and file size limits to prevent "Decompression Bomb" attacks.
    * **Symlink Safety**: Explicitly ignores symbolic links to avoid accidental system file exposure.
* **Modern Python Stack**: Powered by `uv` for lightning-fast, hashed, and reproducible dependency management.
* **Production Logging**: Professional logging instead of simple print statements for better auditing.

## 🚀 Installation

This project requires **Python 3.12+** and is optimized for [uv](https://github.com/astral-sh/uv).

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ac999/bg-remover](https://github.com/ac999/bg-remover)
    cd bg-remover
    ```

2.  **Initialize the environment and install dependencies:**

    Choose the command based on your hardware:

    * **For CPU (Standard Laptops, Mac M1/M2/M3, etc.):**
        ```bash
        uv sync --extra cpu
        ```

    * **For NVIDIA GPU (Requires CUDA installed):**
        ```bash
        uv sync --extra gpu
        ```

3.  **For Development & Testing:**
    Install additional tools for running tests:
    ```bash
    uv sync --extra test --extra cpu
    ```

4.  **For API Server Deployment:**
    Install dependencies for the REST API:
    ```bash
    uv sync --extra server --extra cpu
    ```

## 🧪 Testing

This project follows a Test-Driven Development (TDD) approach. To run the test suite:
```bash
uv run pytest
```

3.  **Locking:** `uv` handles locking automatically via `uv.lock`, ensuring reproducible and secure builds.

## 📖 Usage

The tool follows a **Source Layout** (`src/`) for clean builds. You can run it directly using `uv run`.

### CLI Mode (Batch Processing)
Place your images in a folder named `input_frames` (created automatically if missing) and run:
```bash
uv run bg-remover
```

### Server Mode (REST API) - *Coming Soon*
Once Phase 2 is complete, you will be able to start the secure FastAPI server:
```bash
uv run bg-remover server
```

### Advanced Arguments

You can customize the directories and verbosity:

```bash
uv run bg-remover --input ./my_photos --output ./processed_results --verbose

```

**Options:**

* `-i, --input`: Directory containing source images (Default: `input_frames`).
* `-o, --output`: Directory for transparent PNGs (Default: `frames`).
* `-v, --verbose`: Enables detailed debug logs.

## 🛡️ Security Audit & Best Practices

This tool implements several "expert-level" security measures:

* **Resource Limits**: `Pillow` is configured with `MAX_IMAGE_PIXELS` to prevent memory exhaustion from malicious images.
* **File Validation**: Files are validated by content (magic bytes) through the `Pillow` engine, not just by extension.
* **Hashed Dependencies**: Using `uv.lock` ensures that every package installed matches the exact cryptographic hash recorded, preventing supply-chain attacks.
* **Isolated Builds**: The `src/` layout prevents the build system from accidentally bundling your private data folders (`input_frames`, `frames`) into the distribution.

## 🤖 AI Model Information

On the **first run**, the script will automatically download the `u2net` model (approx. 170MB) from the official `rembg` source.

* **Storage Location**: The model is saved in `~/.u2net/`.
* **Integrity**: The model is managed by the `onnxruntime` backend for secure execution.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

