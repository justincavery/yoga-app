"""
Generate thumbnails for pose images.
Creates 400x400px thumbnails with -thumb suffix.
"""
from pathlib import Path
from PIL import Image
import sys

def generate_thumbnails(source_dir: Path, thumb_size: tuple = (400, 400)):
    """Generate thumbnails for all JPG images in directory."""

    if not source_dir.exists():
        print(f"Error: Directory not found: {source_dir}")
        sys.exit(1)

    # Find all JPG files (exclude backup files)
    image_files = [
        f for f in source_dir.glob("*.jpg")
        if not f.name.endswith(("-thumb.jpg", ".backup.jpg", ".pro-backup.jpg"))
    ]

    if not image_files:
        print(f"No image files found in {source_dir}")
        sys.exit(1)

    print(f"Found {len(image_files)} images to process")
    print(f"Generating {thumb_size[0]}x{thumb_size[1]}px thumbnails...\n")

    success_count = 0
    error_count = 0

    for image_path in image_files:
        try:
            # Open image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (handles RGBA, etc.)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create thumbnail (maintains aspect ratio, fits within size)
                img.thumbnail(thumb_size, Image.Resampling.LANCZOS)

                # Generate thumbnail filename
                thumb_path = image_path.parent / f"{image_path.stem}-thumb.jpg"

                # Save thumbnail with good quality
                img.save(thumb_path, 'JPEG', quality=85, optimize=True)

                print(f"✓ {image_path.name} -> {thumb_path.name} ({img.size[0]}x{img.size[1]}px)")
                success_count += 1

        except Exception as error:
            print(f"✗ Error processing {image_path.name}: {error}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Thumbnail generation complete!")
    print(f"Success: {success_count} thumbnails created")
    if error_count > 0:
        print(f"Errors: {error_count} files failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Get the content/images/poses directory
    script_dir = Path(__file__).parent
    content_dir = script_dir.parent.parent / "content" / "images" / "poses"

    generate_thumbnails(content_dir)
