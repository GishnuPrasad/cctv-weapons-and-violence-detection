from pydantic import BaseModel


class SignupRequest(BaseModel):
    username: str
    name: str
    mobile_number: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str


class CameraCreate(BaseModel):
    camera_name: str
    ip_url: str
