from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from Models.user import User, Token
from Services.auth_service import get_user_by_email, create_user, upload_user_profile_image, update_user
from Utils.hashing import verify_password
from Utils.jwt import create_access_token, decode_access_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return payload["sub"]


@router.post("/register", response_model=Token)
def register_user(
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...)
):
    if get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    user_data = create_user(email, username, password)

    token = create_access_token({"sub": user_data["email"]})
    return Token(
        access_token=token,
        token_type="bearer",
        user={
            "email": user_data["email"],
            "username": user_data["username"],
            "profile_image": user_data["profile_image"]
        }
    )


@router.post("/upload-profile-image", summary="Upload a user profile image")
def upload_profile_image(
    profile_image: UploadFile = File(...),
    user_email: str = Depends(get_current_user)
):
    user = get_user_by_email(user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile_image_url = upload_user_profile_image(user_email, profile_image)
    return {"profile_image": profile_image_url}



@router.post("/token", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user["email"]})
    return Token(
        access_token=token,
        token_type="bearer",
        user={
            "email": user["email"],
            "username": user["username"],
            "profile_image": user["profile_image"]
        }
    )


@router.put("/update-user")
def update_user_info(
        username: str = Form(None),
        password: str = Form(None),
        profile_image: UploadFile = None,
        user_email: str = Depends(get_current_user)
):
    user = get_user_by_email(user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updates = {}
    if username:
        updates["username"] = username
    if password:
        updates["password"] = password
    if profile_image:
        updates["profile_image"] = profile_image

    updated_user = update_user(user_email, updates)

    return {
        "email": updated_user["email"],
        "username": updated_user["username"],
        "profile_image": updated_user.get("profile_image")
    }


@router.get("/current-user", response_model=User)
def get_current_user_info(user_email: str = Depends(get_current_user)):
    user = get_user_by_email(user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user["id"] = str(user["_id"])
    return user
