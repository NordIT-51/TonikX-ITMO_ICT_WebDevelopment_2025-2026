from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class AppStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class TripBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    start_location: str
    destination: str

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    start_location: Optional[str] = None
    destination: Optional[str] = None

class Trip(TripBase):
    id: int
    created_by: int
    created_at: datetime
    creator: Optional[UserInDB] = None
    applications: Optional[List["TripApplication"]] = None

    class Config:
        from_attributes = True

class TripApplicationBase(BaseModel):
    comment: Optional[str] = None

class TripApplicationCreate(TripApplicationBase):
    trip_id: int

class TripApplicationUpdate(BaseModel):
    status: AppStatus

class TripApplication(TripApplicationBase):
    id: int
    user_id: int
    trip_id: int
    status: AppStatus
    applied_at: datetime

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int
    trip_id: int

class Message(MessageBase):
    id: int
    trip_id: int
    sender_id: int
    receiver_id: int
    sent_at: datetime
    sender: Optional[UserInDB] = None
    receiver: Optional[UserInDB] = None
    trip: Optional[Trip] = None

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    rating: float = Field(ge=1.0, le=5.0)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    to_user_id: int
    trip_id: int

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = None

class Review(ReviewBase):
    id: int
    from_user_id: int
    to_user_id: int
    trip_id: int
    created_at: datetime
    from_user: Optional[UserInDB] = None
    to_user: Optional[UserInDB] = None
    trip: Optional[Trip] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Обновление ссылок для вложенных моделей
Trip.model_rebuild()
TripApplication.model_rebuild()
Message.model_rebuild()
Review.model_rebuild()