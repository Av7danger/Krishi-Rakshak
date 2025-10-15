from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class Farmer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone: str = Field(index=True, unique=True)
    name: Optional[str] = None
    hashed_password: str
    consent_for_training: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Report(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    farmer_id: Optional[int] = Field(foreign_key="farmer.id")
    image_path: str
    status: str = Field(default="queued")  # queued|processing|processed|failed
    disease: Optional[str] = None
    confidence: Optional[float] = None
    treatment: Optional[str] = None
    crop_type: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    consent_for_training: bool = False
    processed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Feedback(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    report_id: int = Field(foreign_key="report.id")
    farmer_id: Optional[int] = Field(foreign_key="farmer.id")
    rating: int
    comments: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelVersion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str  # telegram|whatsapp
    external_message_id: Optional[str] = None
    farmer_id: Optional[int] = Field(foreign_key="farmer.id")
    direction: str = "in"  # in|out
    text: Optional[str] = None
    media_url: Optional[str] = None
    payload: Optional[dict] = Field(sa_column=Column(JSON))
    reply_text: Optional[str] = None
    reply_media_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
