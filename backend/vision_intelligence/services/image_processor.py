"""
backend/vision_intelligence/services/image_processor.py
Image Validation, Sanitization, Resizing, and Base64 Pre-processing Service.
"""

import io
import base64
from typing import Tuple
from PIL import Image, ImageOps

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB Limit
MAX_IMAGE_DIMENSION = 2048  # Maximum pixel dimension on longest edge
ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP", "HEIC"}


class ImagePreprocessingError(Exception):
    """Custom exception raised when image validation or conversion fails."""
    pass


def preprocess_image(image_bytes: bytes) -> Tuple[str, str, Tuple[int, int]]:
    """
    Validates, format-checks, auto-orients, resizes, and base64-encodes incoming raw image bytes.

    Args:
        image_bytes: Raw binary bytes of uploaded image.

    Returns:
        Tuple containing:
            - base64_str (str): Clean Base64 encoded JPEG string.
            - mime_type (str): Format MIME type (e.g. "image/jpeg").
            - dimensions (Tuple[int, int]): Final (width, height) tuple.

    Raises:
        ImagePreprocessingError: If file exceeds 10MB, format is invalid, or byte payload is corrupted.
    """
    if not image_bytes:
        raise ImagePreprocessingError("Empty image payload received.")

    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise ImagePreprocessingError(
            f"Image payload size ({len(image_bytes) / (1024 * 1024):.2f} MB) exceeds maximum allowed limit of 10 MB."
        )

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # Verify image integrity
        # Re-open after verify as per PIL documentation requirements
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise ImagePreprocessingError(f"Corrupted or unreadable image file: {str(e)}")

    img_format = (img.format or "JPEG").upper()
    if img_format not in ALLOWED_FORMATS:
        # Fallback format conversion attempt for standard image types
        img_format = "JPEG"

    # Auto-orient based on EXIF camera tags (e.g., mobile captures)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass  # If EXIF reading fails, keep original image orientation

    # Convert non-RGB modes (RGBA, Palette, Grayscale) to standard RGB
    if img.mode in ("RGBA", "P", "LA", "1", "CMYK"):
        img = img.convert("RGB")

    # Resize if longest edge exceeds 2048px while maintaining aspect ratio
    width, height = img.size
    if max(width, height) > MAX_IMAGE_DIMENSION:
        ratio = MAX_IMAGE_DIMENSION / float(max(width, height))
        new_dimensions = (int(width * ratio), int(height * ratio))
        img = img.resize(new_dimensions, Image.Resampling.LANCZOS)
        width, height = img.size

    # Save to memory buffer as optimized JPEG
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True)
    buffer.seek(0)

    # Encode to base64 UTF-8 string
    encoded_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    mime_type = "image/jpeg"

    return encoded_base64, mime_type, (width, height)
