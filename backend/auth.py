import re
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERNAME_REGEX = r"^[A-Za-z][A-Za-z0-9]{5,9}$"
MOBILE_REGEX = r"^\d{10}$"
PASSWORD_REGEX = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
    r"(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"
)


def validate_username(username: str):
    if not re.match(USERNAME_REGEX, username):
        raise HTTPException(
            400,
            "Username must start with a letter, contain only letters and numbers, "
            "and be 6–10 characters long."
        )


def validate_mobile(mobile: str):
    if not re.match(MOBILE_REGEX, mobile):
        raise HTTPException(400, "Mobile number must contain exactly 10 digits.")


def validate_password(password: str):
    if not re.match(PASSWORD_REGEX, password):
        raise HTTPException(
            400,
            "Password must be at least 8 characters long and include "
            "uppercase, lowercase, number, and special character."
        )


def hash_password(password: str) -> str:
    safe_password = password.encode("utf-8")[:72]
    return pwd_context.hash(safe_password)


def verify_password(password: str, hashed: str) -> bool:
    safe_password = password.encode("utf-8")[:72]
    return pwd_context.verify(safe_password, hashed)
