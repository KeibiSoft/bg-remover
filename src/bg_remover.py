import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from PIL import Image, UnidentifiedImageError
from rembg import remove

# --- SECURITY & CONFIGURATION CONSTANTS ---
# Prevent Decompression Bombs (DoS attacks via massive images)
Image.MAX_IMAGE_PIXELS = 89_478_485  # Approx. 90 megapixels limit

# Limit maximum file size (e.g., 20 MB) to prevent memory exhaustion
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024

# Allowed output formats
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

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
    # 1. Check if it's a symlink to prevent reading outside intended directories
    if file_path.is_symlink():
        logger.warning(f"Skipping symlink: {file_path.name}")
        return False
    
    # 2. Check path traversal (ensure file is actually inside input_dir)
    try:
        resolved_path = file_path.resolve(strict=True)
        resolved_input = input_dir.resolve(strict=True)
        # Fix: Use is_relative_to for robust containment check (avoids prefix match bypass)
        if not resolved_path.is_relative_to(resolved_input):
            logger.warning(f"Path traversal attempt detected: {file_path.name}")
            return False
    except Exception as e:
        logger.debug(f"Path resolution error for {file_path.name}: {e}")
        return False

    # 3. Check file size
    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        logger.warning(f"File too large, skipping: {file_path.name}")
        return False

    # 4. Check basic extension (further validation is done by PIL)
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False

    return True

def process_images(input_dir_str: str, output_dir_str: str, logger: logging.Logger) -> None:
    """Main function to process images and remove backgrounds."""
    input_dir = Path(input_dir_str)
    output_dir = Path(output_dir_str)

    # Validate input directory
    if not input_dir.is_dir():
        logger.error(f"Input directory does not exist or is not a directory: {input_dir}")
        sys.exit(1)

    # Securely create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing local AI model. Note: First run will download the model (~170MB).")

    processed_count = 0
    error_count = 0

    # Iterate through files securely
    for file_path in input_dir.iterdir():
        if not file_path.is_file():
            continue

        if not is_safe_file(file_path, input_dir, logger):
            continue

        output_filename = f"{file_path.stem}.png"
        output_path = output_dir / output_filename

        logger.info(f"Processing: {file_path.name} -> {output_filename}")

        try:
            # Use context manager to ensure file descriptors are securely closed
            with Image.open(file_path) as input_image:
                # remove() returns a new PIL Image
                output_image = remove(input_image)
                
                # Save as PNG to preserve alpha channel (transparency)
                output_image.save(output_path, format="PNG")
                processed_count += 1
                
        except UnidentifiedImageError:
            logger.warning(f"File is not a valid image or is corrupted: {file_path.name}")
            error_count += 1
        except Exception as e:
            # Catching general exceptions but logging securely to avoid info leakage.
            # Detailed trace is only available in debug mode.
            logger.error(f"Failed to process {file_path.name}. Set --verbose for details.")
            logger.debug(f"Full error while processing {file_path.name}: {e}", exc_info=True)
            error_count += 1

    logger.info("========================================")
    logger.info(f"Task Completed! Successfully processed: {processed_count}, Errors: {error_count}")
    logger.info(f"Output saved to: {output_dir.resolve()}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch background removal tool using local AI.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-i", "--input", 
        type=str, 
        default="input_frames",
        help="Path to the directory containing input images."
    )
    parser.add_argument(
        "-o", "--output", 
        type=str, 
        default="frames",
        help="Path to the directory where transparent PNGs will be saved."
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose/debug logging."
    )

    args = parser.parse_args()
    logger = setup_logging(args.verbose)

    process_images(args.input, args.output, logger)

if __name__ == "__main__":
    main()
