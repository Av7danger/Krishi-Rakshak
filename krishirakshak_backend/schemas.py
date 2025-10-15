from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FarmerCreate(BaseModel):
    phone: str
    name: Optional[str] = None
    password: str
    consent_for_training: bool = False


class FarmerOut(BaseModel):
    id: int
    phone: str
    name: Optional[str] = None
    consent_for_training: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    phone: str
    password: str


class ReportCreate(BaseModel):
    crop_type: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    consent_for_training: bool = False


class ReportOut(BaseModel):
    id: int
    farmer_id: Optional[int]
    image_path: str
    status: str
    disease: Optional[str]
    confidence: Optional[float]
    treatment: Optional[str]
    crop_type: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    consent_for_training: bool
    processed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    report_id: int
    rating: int
    comments: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    report_id: int
    farmer_id: Optional[int]
    rating: int
    comments: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
