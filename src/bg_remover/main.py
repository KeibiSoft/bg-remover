import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from PIL import Image, UnidentifiedImageError
from bg_remover.core import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    remove_bg_from_stream,
    verify_image_signature
)

def setup_logging(verbose: bool) -> logging.Logger:
    """Configures the logging level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)

def is_safe_file(file_path: Path, input_dir: Path, logger: logging.Logger) -> bool:
    """Performs security checks on the file before processing."""
    if file_path.is_symlink():
        logger.warning(f"Skipping symlink: {file_path.name}")
        return False
    
    try:
        resolved_path = file_path.resolve(strict=True)
        resolved_input = input_dir.resolve(strict=True)
        if not resolved_path.is_relative_to(resolved_input):
            logger.warning(f"Path traversal attempt detected: {file_path.name}")
            return False
    except Exception as e:
        logger.debug(f"Path resolution error for {file_path.name}: {e}")
        return False

    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        logger.warning(f"File too large, skipping: {file_path.name}")
        return False

    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False

    return True

def process_images(input_dir_str: str, output_dir_str: str, logger: logging.Logger) -> None:
    """Main function to process images and remove backgrounds."""
    input_dir = Path(input_dir_str)
    output_dir = Path(output_dir_str)

    if not input_dir.is_dir():
        logger.error(f"Input directory does not exist or is not a directory: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Initializing local AI model. Note: First run will download the model (~170MB).")

    processed_count = 0
    error_count = 0

    for file_path in input_dir.iterdir():
        if not file_path.is_file() or not is_safe_file(file_path, input_dir, logger):
            continue

        output_filename = f"{file_path.stem}.png"
        output_path = output_dir / output_filename

        logger.info(f"Processing: {file_path.name} -> {output_filename}")

        try:
            with open(file_path, "rb") as f:
                import io
                input_stream = io.BytesIO(f.read())
                
                # Security: Magic byte validation
                if not verify_image_signature(input_stream):
                    logger.warning(f"File signature mismatch, skipping: {file_path.name}")
                    error_count += 1
                    continue
                
                output_stream = remove_bg_from_stream(input_stream)
                
                # Save processed image
                with open(output_path, "wb") as out_f:
                    out_f.write(output_stream.getbuffer())
                
                processed_count += 1
                
        except UnidentifiedImageError:
            logger.warning(f"File is not a valid image or is corrupted: {file_path.name}")
            error_count += 1
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}. Set --verbose for details.")
            logger.debug(f"Full error while processing {file_path.name}: {e}", exc_info=True)
            error_count += 1

    logger.info("========================================")
    logger.info(f"Task Completed! Successfully processed: {processed_count}, Errors: {error_count}")
    logger.info(f"Output saved to: {output_dir.resolve()}")

def run_server(host: str, port: int, verbose: bool):
    """Starts the FastAPI server."""
    import uvicorn
    # Use the absolute import path for uvicorn
    uvicorn.run("bg_remover.api.routes:app", host=host, port=port, reload=False, log_level="debug" if verbose else "info")

def main() -> None:
    # Environment-based mode switching (convenient for Docker)
    if os.getenv("BG_REMOVER_MODE") == "server":
        port = int(os.getenv("PORT", 8000))
        verbose = os.getenv("VERBOSE", "false").lower() == "true"
        run_server("0.0.0.0", port, verbose)
        return

    parser = argparse.ArgumentParser(
        description="Secure local AI tool for batch background removal.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Modes of operation")
    
    # CLI Mode Subparser
    cli_parser = subparsers.add_parser("cli", help="Batch process local images")
    cli_parser.add_argument(
        "-i", "--input", 
        type=str, 
        default="input_frames",
        help="Path to the directory containing input images."
    )
    cli_parser.add_argument(
        "-o", "--output", 
        type=str, 
        default="frames",
        help="Path to the directory where transparent PNGs will be saved."
    )
    cli_parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose/debug logging."
    )

    # Server Mode Subparser
    server_parser = subparsers.add_parser("server", help="Start the REST API server")
    server_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    server_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Routing
    if args.command == "server":
        setup_logging(args.verbose)
        run_server(args.host, args.port, args.verbose)
    elif args.command == "cli":
        logger = setup_logging(args.verbose)
        process_images(args.input, args.output, logger)

if __name__ == "__main__":
    main()
