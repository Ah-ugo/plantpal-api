import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import HTTPException
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)


def upload_to_cloudinary(file_path: str) -> str:
    """
    Upload a file to Cloudinary and return its URL.
    """
    response = cloudinary.uploader.upload(file_path, folder="shops", resource_type="raw")
    return response.get("url")