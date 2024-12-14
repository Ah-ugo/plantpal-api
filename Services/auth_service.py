from DB.database import db
from Utils.hashing import hash_password, verify_password
from Utils.jwt import create_access_token
from Utils.cloudinary_upload import upload_to_cloudinary


def get_user_by_email(email: str):
    return db.users.find_one({"email": email})


def create_user(email: str, username: str, password: str):
    hashed_password = hash_password(password)
    user_data = {
        "email": email,
        "username": username,
        "hashed_password": hashed_password,
        "profile_image": None
    }
    result = db.users.insert_one(user_data)
    user_data["id"] = str(result.inserted_id)
    return user_data


def upload_user_profile_image(user_email: str, profile_image):
    profile_image_url = upload_to_cloudinary(profile_image)
    db.users.update_one(
        {"email": user_email},
        {"$set": {"profile_image": profile_image_url}}
    )
    return profile_image_url


def update_user(email: str, updates: dict):
    if "password" in updates:
        updates["hashed_password"] = hash_password(updates.pop("password"))
    if "profile_image" in updates:
        updates["profile_image"] = upload_to_cloudinary(updates.pop("profile_image"))

    db.users.update_one({"email": email}, {"$set": updates})
    updated_user = db.users.find_one({"email": email})
    updated_user["id"] = str(updated_user["_id"])
    return updated_user
