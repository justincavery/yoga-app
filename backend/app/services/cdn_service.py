"""
CDN service for YogaFlow.
Handles CDN URL generation for static assets (images, videos).
"""
from typing import Optional
from app.core.config import settings
from app.core.logging_config import logger


class CDNService:
    """
    Service for generating CDN URLs for static assets.
    Supports local development and production CDN configurations.
    """

    def get_image_url(self, path: str) -> str:
        """
        Get CDN URL for an image.

        Args:
            path: Relative image path (e.g., 'poses/warrior-pose.jpg')

        Returns:
            str: Full CDN URL or local URL if CDN disabled

        Examples:
            >>> cdn_service.get_image_url('poses/warrior-pose.jpg')
            'https://cdn.yogaflow.app/images/poses/warrior-pose.jpg'

            >>> cdn_service.get_image_url('/poses/warrior-pose.jpg')  # Leading slash ok
            'https://cdn.yogaflow.app/images/poses/warrior-pose.jpg'
        """
        # Remove leading slash if present
        clean_path = path.lstrip('/')

        if not settings.cdn_enabled:
            return f"/images/{clean_path}"

        return f"{settings.cdn_base_url}/images/{clean_path}"

    def get_thumbnail_url(
        self,
        path: str,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> str:
        """
        Get CDN URL for image thumbnail with optional resizing.

        Args:
            path: Relative image path
            width: Optional thumbnail width in pixels
            height: Optional thumbnail height in pixels

        Returns:
            str: Full CDN URL for thumbnail

        Note:
            Image resizing requires CloudFlare paid plan or custom image processor.
            For MVP, returns standard image URL.
        """
        # For MVP, return standard image URL
        # TODO: Implement image resizing when CDN supports it
        base_url = self.get_image_url(path)

        if width or height:
            logger.debug(
                f"Image resizing requested but not yet implemented: {path}",
                width=width,
                height=height
            )

        return base_url

    def get_video_url(self, path: str) -> str:
        """
        Get CDN URL for a video.

        Args:
            path: Relative video path (e.g., 'tutorials/sun-salutation.mp4')

        Returns:
            str: Full CDN URL or local URL if CDN disabled
        """
        # Remove leading slash if present
        clean_path = path.lstrip('/')

        if not settings.cdn_enabled:
            return f"/videos/{clean_path}"

        return f"{settings.cdn_base_url}/videos/{clean_path}"

    def get_asset_url(self, path: str, asset_type: str = "static") -> str:
        """
        Get CDN URL for any static asset.

        Args:
            path: Relative asset path
            asset_type: Asset type directory (e.g., 'static', 'downloads')

        Returns:
            str: Full CDN URL or local URL if CDN disabled
        """
        # Remove leading slash if present
        clean_path = path.lstrip('/')

        if not settings.cdn_enabled:
            return f"/{asset_type}/{clean_path}"

        return f"{settings.cdn_base_url}/{asset_type}/{clean_path}"

    def is_cdn_enabled(self) -> bool:
        """
        Check if CDN is enabled.

        Returns:
            bool: True if CDN is enabled, False otherwise
        """
        return settings.cdn_enabled

    def get_cache_control_header(self, asset_type: str = "image") -> str:
        """
        Get appropriate Cache-Control header for asset type.

        Args:
            asset_type: Type of asset (image, video, static)

        Returns:
            str: Cache-Control header value
        """
        cache_headers = {
            "image": "public, max-age=31536000, immutable",  # 1 year
            "video": "public, max-age=31536000, immutable",  # 1 year
            "static": "public, max-age=86400",  # 1 day
            "dynamic": "public, max-age=300",  # 5 minutes
        }

        return cache_headers.get(asset_type, cache_headers["static"])


# Global CDN service instance
cdn_service = CDNService()
