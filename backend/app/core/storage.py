import aioboto3
from fastapi import UploadFile
from app.core.config import settings

class S3Storage:
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.R2_UPLOAD_FILES_BUCKET_NAME
        self.endpoint_url = settings.R2_UPLOAD_FILES_ENDPOINT_URL
        self.access_key = settings.R2_UPLOAD_FILES_ACCESS_KEY_ID
        self.secret_key = settings.R2_UPLOAD_FILES_SECRET_ACCESS_KEY
        self.public_url = settings.R2_UPLOAD_FILES_PUBLIC_URL.rstrip("/")

    async def upload_file(self, file: UploadFile, key: str) -> str:
        """
        Uploads a file to R2 and returns the public URL.
        """
        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as s3:
            content = await file.read()
            await s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=file.content_type,
            )
            
        return f"{self.public_url}/{key}"

    def get_public_url(self, key: str) -> str:
        """
        Returns the public URL for a given key.
        """
        if not key:
            return ""
        if key.startswith("http"):
            return key
        return f"{self.public_url}/{key}"

storage = S3Storage()
