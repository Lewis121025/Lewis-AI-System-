"""MinIO/S3 object storage helpers."""

from __future__ import annotations

import logging
from typing import Optional

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

LOGGER = logging.getLogger(__name__)


class ObjectStorageClient:
    """Thin wrapper around boto3 for interacting with object storage."""

    def __init__(self, bucket: Optional[str] = None) -> None:
        settings = get_settings()
        self.bucket = bucket or settings.s3_bucket
        session = boto3.session.Session()
        self._client = session.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            config=Config(signature_version="s3v4"),
        )

    @property
    def client(self):
        """Expose underlying boto3 client."""
        return self._client

    def ensure_bucket(self) -> None:
        """Create the bucket if it does not already exist."""
        try:
            self._client.head_bucket(Bucket=self.bucket)
        except ClientError:
            LOGGER.info("Creating bucket %s", self.bucket)
            self._client.create_bucket(Bucket=self.bucket)

    def upload_bytes(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        """Upload raw bytes to object storage and return the object key."""
        extra_args = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata
        try:
            self._client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra_args)
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover - network
            LOGGER.exception("Failed to upload object %s: %s", key, exc)
            raise
        return key

    def download_bytes(self, key: str) -> bytes:
        """Download object bytes."""
        try:
            response = self._client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover - network
            LOGGER.exception("Failed to download object %s: %s", key, exc)
            raise

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access."""
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover - network
            LOGGER.exception("Failed to create presigned URL for %s: %s", key, exc)
            raise
