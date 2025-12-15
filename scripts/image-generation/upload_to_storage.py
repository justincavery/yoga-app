#!/usr/bin/env python3
"""
Upload generated pose images to cloud storage and update database.

Supports:
- AWS S3
- Cloudflare R2
- Local file storage (for development)

Requirements:
    pip install boto3 psycopg2-binary
"""

import os
import sys
import json
import mimetypes
from pathlib import Path
import argparse
import boto3
from botocore.exceptions import ClientError

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from app.core.config import settings


class StorageUploader:
    def __init__(self, provider="s3", bucket=None, base_url=None):
        """
        Initialize storage uploader.

        Args:
            provider: Storage provider ('s3', 'r2', or 'local')
            bucket: Bucket/container name
            base_url: Base URL for accessing uploaded files
        """
        self.provider = provider
        self.bucket = bucket
        self.base_url = base_url

        if provider in ["s3", "r2"]:
            # Configure boto3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                endpoint_url=os.environ.get('S3_ENDPOINT_URL'),  # For R2
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )

            if not bucket:
                raise ValueError("Bucket name required for S3/R2 storage")

        elif provider == "local":
            self.local_path = Path(base_url or "./storage/poses")
            self.local_path.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file_path, object_name=None):
        """
        Upload a file to storage.

        Args:
            file_path: Path to file to upload
            object_name: S3 object name (default: same as file_path basename)

        Returns:
            Public URL of uploaded file
        """
        if not object_name:
            object_name = Path(file_path).name

        if self.provider == "local":
            # Copy to local storage
            import shutil
            dest = self.local_path / object_name
            shutil.copy(file_path, dest)
            return str(dest)

        # Upload to S3/R2
        try:
            # Guess content type
            content_type, _ = mimetypes.guess_type(file_path)
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            # Make public readable
            extra_args['ACL'] = 'public-read'

            self.s3_client.upload_file(
                file_path,
                self.bucket,
                f"poses/{object_name}",
                ExtraArgs=extra_args
            )

            # Return public URL
            if self.base_url:
                return f"{self.base_url}/poses/{object_name}"
            else:
                return f"https://{self.bucket}.s3.amazonaws.com/poses/{object_name}"

        except ClientError as e:
            print(f"Error uploading {file_path}: {e}")
            return None


def update_database(pose_updates):
    """
    Update database with new image URLs.

    Args:
        pose_updates: Dict mapping pose names to list of image URLs
    """
    import psycopg2
    import psycopg2.extras

    try:
        conn = psycopg2.connect(
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        cur = conn.cursor()

        updated = 0
        for pose_name, image_urls in pose_updates.items():
            cur.execute(
                """
                UPDATE poses
                SET image_urls = %s
                WHERE name = %s
                RETURNING id
                """,
                (json.dumps(image_urls), pose_name)
            )

            if cur.fetchone():
                updated += 1
                print(f"  Updated: {pose_name} ({len(image_urls)} images)")

        conn.commit()
        conn.close()

        print(f"\n✓ Database updated: {updated} poses")

    except Exception as e:
        print(f"Error updating database: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Upload generated pose images to cloud storage"
    )
    parser.add_argument(
        "--input", type=str, default="generated_poses",
        help="Directory containing generated images"
    )
    parser.add_argument(
        "--provider", type=str, default="local",
        choices=["s3", "r2", "local"],
        help="Storage provider (default: local)"
    )
    parser.add_argument(
        "--bucket", type=str,
        help="S3/R2 bucket name"
    )
    parser.add_argument(
        "--base-url", type=str,
        help="Base URL for uploaded files"
    )
    parser.add_argument(
        "--update-db", action="store_true",
        help="Update database with new URLs"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be uploaded without actually uploading"
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    # Load manifest
    manifest_path = input_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"Error: manifest.json not found in {input_dir}")
        print("Make sure you've run the generation script first.")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Initialize uploader
    if not args.dry_run:
        uploader = StorageUploader(
            provider=args.provider,
            bucket=args.bucket,
            base_url=args.base_url
        )

    print(f"\nUploading images from: {input_dir}")
    print(f"Provider: {args.provider}")
    if args.bucket:
        print(f"Bucket: {args.bucket}")
    print(f"Dry run: {args.dry_run}\n")

    pose_updates = {}
    total_files = sum(len(paths) for paths in manifest.values())
    uploaded = 0

    for pose_name, image_paths in manifest.items():
        print(f"Processing: {pose_name} ({len(image_paths)} images)")

        if isinstance(image_paths, dict):
            image_paths = image_paths.get('paths', [])

        uploaded_urls = []

        for img_path in image_paths:
            file_path = Path(img_path)

            if not file_path.exists():
                print(f"  Warning: File not found: {file_path}")
                continue

            if args.dry_run:
                print(f"  Would upload: {file_path.name}")
                uploaded_urls.append(f"https://example.com/poses/{file_path.name}")
            else:
                url = uploader.upload_file(str(file_path))
                if url:
                    uploaded_urls.append(url)
                    print(f"  Uploaded: {file_path.name}")
                    uploaded += 1

        pose_updates[pose_name] = uploaded_urls

    print(f"\n{'='*60}")
    if args.dry_run:
        print("DRY RUN - No files were actually uploaded")
    else:
        print(f"✓ Upload complete: {uploaded}/{total_files} files")

    # Update database if requested
    if args.update_db:
        if args.dry_run:
            print("\nDRY RUN - Would update database with:")
            for pose_name, urls in pose_updates.items():
                print(f"  {pose_name}: {len(urls)} images")
        else:
            print("\nUpdating database...")
            update_database(pose_updates)

    # Save updated manifest with URLs
    output_manifest = input_dir / "uploaded_manifest.json"
    with open(output_manifest, 'w') as f:
        json.dump(pose_updates, f, indent=2)

    print(f"\nManifest saved: {output_manifest}")

    if not args.update_db:
        print("\nTo update the database, run:")
        print(f"  python {sys.argv[0]} --input {args.input} --update-db")


if __name__ == "__main__":
    main()
