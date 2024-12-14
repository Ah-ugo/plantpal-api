import cloudinary
import cloudinary.uploader
from fastapi import HTTPException
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

def upload_to_cloudinary(file):
    try:
        response = cloudinary.uploader.upload(
            file.file,
            folder="shops",
            resource_type="raw"
        )
        return response.get("url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")
