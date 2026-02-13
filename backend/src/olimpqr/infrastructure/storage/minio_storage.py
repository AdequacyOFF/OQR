"""MinIO storage service for files (PDFs, scans)."""

from io import BytesIO
from typing import BinaryIO
from minio import Minio
from minio.error import S3Error

from ...config import settings


class MinIOStorage:
    """MinIO S3-compatible storage service."""

    def __init__(self):
        """Initialize MinIO client."""
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self._ensure_buckets()

    def _ensure_buckets(self):
        """Ensure required buckets exist."""
        buckets = [
            settings.minio_bucket_sheets,
            settings.minio_bucket_scans
        ]
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    print(f"Created MinIO bucket: {bucket}")
            except S3Error as e:
                print(f"Error creating bucket {bucket}: {e}")

    def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: bytes | BinaryIO,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload file to MinIO.

        Args:
            bucket: Bucket name
            object_name: Object name (path) in bucket
            data: File data (bytes or file-like object)
            content_type: Content type of the file

        Returns:
            Object path in bucket

        Raises:
            S3Error: If upload fails
        """
        # Convert bytes to BytesIO if needed
        if isinstance(data, bytes):
            data = BytesIO(data)
            length = len(data.getvalue())
        else:
            # For file-like objects, seek to end to get length
            current_pos = data.tell()
            data.seek(0, 2)  # Seek to end
            length = data.tell()
            data.seek(current_pos)  # Restore position

        # Upload file
        self.client.put_object(
            bucket,
            object_name,
            data,
            length=length,
            content_type=content_type
        )

        return object_name

    def download_file(self, bucket: str, object_name: str) -> bytes:
        """Download file from MinIO.

        Args:
            bucket: Bucket name
            object_name: Object name (path) in bucket

        Returns:
            File data as bytes

        Raises:
            S3Error: If download fails
        """
        response = self.client.get_object(bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires_seconds: int = 3600
    ) -> str:
        """Generate presigned URL for file access.

        Args:
            bucket: Bucket name
            object_name: Object name (path) in bucket
            expires_seconds: URL expiration time in seconds

        Returns:
            Presigned URL

        Raises:
            S3Error: If URL generation fails
        """
        from datetime import timedelta
        url = self.client.presigned_get_object(
            bucket,
            object_name,
            expires=timedelta(seconds=expires_seconds)
        )
        return url

    def delete_file(self, bucket: str, object_name: str):
        """Delete file from MinIO.

        Args:
            bucket: Bucket name
            object_name: Object name (path) in bucket

        Raises:
            S3Error: If deletion fails
        """
        self.client.remove_object(bucket, object_name)

    def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists in MinIO.

        Args:
            bucket: Bucket name
            object_name: Object name (path) in bucket

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False
