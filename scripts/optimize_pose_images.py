#!/usr/bin/env python3
"""
Optimize pose images to high-quality JPEG format.
Converts PNG to JPEG at 95% quality (near-lossless) while reducing file size.
"""
import sys
from pathlib import Path
from PIL import Image

# Directories
POSES_DIR = Path(__file__).parent.parent / "content" / "images" / "poses"

# Settings
JPEG_QUALITY = 95  # High quality for near-lossless
MAX_SIZE = 200 * 1024  # 200KB in bytes
MIN_QUALITY = 85  # Don't go below this quality


def optimize_image(input_path: Path):
    """Convert and optimize image to JPEG."""
    try:
        # Skip if already JPEG
        if input_path.suffix.lower() in ['.jpg', '.jpeg']:
            print(f"Skipping {input_path.name} (already JPEG)")
            return False

        with Image.open(input_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Create output path
            output_path = input_path.with_suffix('.jpg')

            # Try to save at high quality first
            quality = JPEG_QUALITY
            img.save(output_path, 'JPEG', quality=quality, optimize=True)

            # If file is too large, reduce quality incrementally
            file_size = output_path.stat().st_size
            while file_size > MAX_SIZE and quality > MIN_QUALITY:
                quality -= 5
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                file_size = output_path.stat().st_size

            final_size_kb = file_size / 1024
            original_size_kb = input_path.stat().st_size / 1024
            reduction = ((original_size_kb - final_size_kb) / original_size_kb) * 100

            print(f"  {input_path.name} -> {output_path.name}")
            print(f"    Quality: {quality}% | Size: {final_size_kb:.1f}KB (was {original_size_kb:.1f}KB, {reduction:.1f}% reduction)")

            # Delete original PNG
            input_path.unlink()
            print(f"    Deleted original PNG")

            return True

    except Exception as error:
        print(f"  Error processing {input_path.name}: {error}")
        return False


def main():
    """Optimize all PNG images in poses directory."""

    # Find all PNG files
    png_files = [f for f in POSES_DIR.iterdir() if f.suffix.lower() == '.png']

    if not png_files:
        print(f"No PNG files found in {POSES_DIR}")
        sys.exit(0)

    print(f"Found {len(png_files)} PNG images to optimize")
    print(f"Target: High-quality JPEG (95% quality) under 200KB\n")

    success_count = 0
    failed_count = 0

    for png_file in sorted(png_files):
        print(f"Processing: {png_file.name}")
        if optimize_image(png_file):
            success_count += 1
        else:
            failed_count += 1
        print()

    print(f"{'='*60}")
    print(f"Complete! Optimized {success_count} images")
    if failed_count > 0:
        print(f"Failed: {failed_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
