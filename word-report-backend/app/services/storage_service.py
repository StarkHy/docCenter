import os
import uuid
from typing import Optional
from datetime import timedelta
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from app.core.config import settings


class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET
        self._init_bucket()
    
    def _init_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                print(f"✅ Created bucket: {self.bucket}")
            else:
                print(f"✅ Bucket exists: {self.bucket}")
        except S3Error as e:
            print(f"❌ Bucket initialization error: {e}")
    
    def _generate_object_name(self, prefix: str, file_name: str) -> str:
        ext = os.path.splitext(file_name)[1] if file_name else ""
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return f"{prefix}/{unique_name}"
    
    async def upload_file(self, prefix: str, file_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        object_name = self._generate_object_name(prefix, file_name)
        
        try:
            if isinstance(file_data, bytes):
                file_data = BytesIO(file_data)
            
            self.client.put_object(
                self.bucket,
                object_name,
                file_data,
                length=-1,
                part_size=5 * 1024 * 1024,
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            raise Exception(f"Upload failed: {e}")
        except Exception as e:
            raise Exception(f"Upload failed: {e}")
    
    async def upload_file_from_path(self, prefix: str, file_path: str) -> str:
        object_name = self._generate_object_name(prefix, os.path.basename(file_path))
        
        try:
            self.client.fput_object(self.bucket, object_name, file_path)
            return object_name
        except S3Error as e:
            raise Exception(f"Upload failed: {e}")
    
    async def download_file(self, object_name: str) -> bytes:
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            raise Exception(f"Download failed: {e}")
    
    async def delete_file(self, object_name: str) -> bool:
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error as e:
            raise Exception(f"Delete failed: {e}")
    
    async def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        try:
            url = self.client.presigned_get_object(self.bucket, object_name, expires=timedelta(seconds=expires))
            return url
        except S3Error as e:
            raise Exception(f"URL generation failed: {e}")
    
    async def file_exists(self, object_name: str) -> bool:
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except S3Error:
            return False
    
    async def get_file_size(self, object_name: str) -> int:
        try:
            stat = self.client.stat_object(self.bucket, object_name)
            return stat.size
        except S3Error:
            return 0
    
    def get_full_path(self, object_name: str) -> str:
        return f"minio://{self.bucket}/{object_name}"


storage_service = StorageService()