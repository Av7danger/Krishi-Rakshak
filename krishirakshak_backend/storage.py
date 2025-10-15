from pathlib import Path
from typing import BinaryIO, Optional
from datetime import timedelta
import os
from .config import settings
from .utils import ensure_upload_dir

try:
    from minio import Minio  # type: ignore
except Exception:  # pragma: no cover
    Minio = None  # type: ignore

try:
    import boto3  # type: ignore
    from botocore.client import Config as BotoConfig  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None  # type: no cover
    BotoConfig = None  # type: no cover


class Storage:
    def __init__(self) -> None:
        self.use_minio = settings.USE_MINIO
        self.bucket = settings.MINIO_BUCKET
        self._minio_client = None
        self._s3_client = None
        if self.use_minio:
            # Prefer MinIO SDK, else boto3 S3 compatible
            if Minio is not None:
                endpoint = settings.MINIO_ENDPOINT
                secure = False if ":" in endpoint else True
                self._minio_client = Minio(
                    endpoint,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=secure,
                )
                # ensure bucket
                found = self._minio_client.bucket_exists(self.bucket)
                if not found:
                    self._minio_client.make_bucket(self.bucket)
            elif boto3 is not None:
                self._s3_client = boto3.client(
                    "s3",
                    endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
                    aws_access_key_id=settings.MINIO_ACCESS_KEY,
                    aws_secret_access_key=settings.MINIO_SECRET_KEY,
                    config=BotoConfig(signature_version="s3v4"),
                )
                # ensure bucket
                existing = self._s3_client.list_buckets().get("Buckets", [])
                if not any(b["Name"] == self.bucket for b in existing):
                    self._s3_client.create_bucket(Bucket=self.bucket)
            else:
                # Fallback to local if no clients available
                self.use_minio = False

        if not self.use_minio:
            ensure_upload_dir()

    def save_file(self, fileobj: BinaryIO, filename: str) -> str:
        data = fileobj.read()
        if self.use_minio and self._minio_client is not None:
            # object key can include simple subfolders
            object_name = filename
            self._minio_client.put_object(
                self.bucket, object_name, data=bytes(data), length=len(data)
            )
            return f"s3://{self.bucket}/{object_name}"
        if self.use_minio and self._s3_client is not None:
            object_name = filename
            self._s3_client.put_object(Bucket=self.bucket, Key=object_name, Body=data)
            return f"s3://{self.bucket}/{object_name}"

        # Local FS fallback
        path = Path(settings.LOCAL_UPLOAD_DIR) / filename
        with open(path, "wb") as f:
            f.write(data)
        return str(path)

    def generate_signed_url(self, object_path: str, expires_seconds: int = 3600) -> Optional[str]:
        if not self.use_minio:
            return None
        # object_path is expected like s3://bucket/key or just key
        key = object_path
        if object_path.startswith("s3://"):
            key = object_path.split("/", 3)[-1]
        if self._minio_client is not None:
            return self._minio_client.presigned_get_object(self.bucket, key, expires=timedelta(seconds=expires_seconds))
        if self._s3_client is not None:
            return self._s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_seconds,
            )
        return None

    def download_to_local(self, object_path: str, dest_path: Optional[str] = None) -> str:
        # For s3 paths, download via client; for local paths, just return path
        if object_path.startswith("s3://"):
            key = object_path.split("/", 3)[-1]
            target = dest_path or str(Path(settings.LOCAL_UPLOAD_DIR) / key.replace("/", "_"))
            if self._minio_client is not None:
                with open(target, "wb") as f:
                    data = self._minio_client.get_object(self.bucket, key)
                    try:
                        for d in data.stream(32 * 1024):
                            f.write(d)
                    finally:
                        data.close()
                        data.release_conn()
                return target
            if self._s3_client is not None:
                self._s3_client.download_file(self.bucket, key, target)
                return target
        return object_path


storage = Storage()
