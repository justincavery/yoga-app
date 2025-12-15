#!/usr/bin/env python3
"""
Generate thumbnails from pose images.
Creates 400x400 JPEG thumbnails at 80% quality.
"""
import sys
from pathlib import Path
from PIL import Image

# Directories
POSES_DIR = Path(__file__).parent.parent / "content" / "images" / "poses"
THUMBNAILS_DIR = Path(__file__).parent.parent / "content" / "images" / "thumbnails"

# Thumbnail settings
THUMBNAIL_SIZE = (400, 400)
JPEG_QUALITY = 80


def create_thumbnail(input_path: Path, output_path: Path):
    """Create a square thumbnail from an image."""
    try:
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if needed (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Calculate dimensions for center crop to square
            width, height = img.size
            min_dim = min(width, height)

            # Center crop to square
            left = (width - min_dim) // 2
            top = (height - min_dim) // 2
            right = left + min_dim
            bottom = top + min_dim

            img_cropped = img.crop((left, top, right, bottom))

            # Resize to thumbnail size with high-quality resampling
            img_thumbnail = img_cropped.resize(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

            # Save as JPEG
            img_thumbnail.save(
                output_path,
                'JPEG',
                quality=JPEG_QUALITY,
                optimize=True
            )

            return True
    except Exception as error:
        print(f"Error processing {input_path.name}: {error}")
        return False


def main():
    """Generate thumbnails for all images in poses directory."""

    # Ensure thumbnails directory exists
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    image_files = [
        f for f in POSES_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        print(f"No images found in {POSES_DIR}")
        sys.exit(1)

    print(f"Found {len(image_files)} images in poses directory")
    print(f"Generating {THUMBNAIL_SIZE[0]}x{THUMBNAIL_SIZE[1]} thumbnails at {JPEG_QUALITY}% quality\n")

    success_count = 0
    failed_count = 0

    for img_file in sorted(image_files):
        # Create output filename (always .jpg)
        output_filename = img_file.stem + '.jpg'
        output_path = THUMBNAILS_DIR / output_filename

        print(f"Processing: {img_file.name} -> {output_filename}", end=" ... ")

        if create_thumbnail(img_file, output_path):
            file_size = output_path.stat().st_size / 1024  # KB
            print(f"✓ ({file_size:.1f} KB)")
            success_count += 1
        else:
            print("✗ Failed")
            failed_count += 1

    print(f"\n{'='*60}")
    print(f"Complete! Generated {success_count} thumbnails")
    if failed_count > 0:
        print(f"Failed: {failed_count}")
    print(f"{'='*60}")
    print(f"\nThumbnails saved to: {THUMBNAILS_DIR}")


if __name__ == "__main__":
    main()
