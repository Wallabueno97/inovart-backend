from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, time
import uuid

# Admin Model
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashedPassword: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)

# Service Model
class ServiceBase(BaseModel):
    name: str
    description: str
    features: List[str] = []

class Service(ServiceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None

# Part Model
class PartBase(BaseModel):
    name: str
    description: str
    category: str
    image: str
    inStock: bool = True
    price: Optional[float] = None

class Part(PartBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class PartUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    inStock: Optional[bool] = None
    price: Optional[float] = None

# Review Model
class ReviewBase(BaseModel):
    name: str
    rating: int = Field(ge=1, le=5)
    comment: str

class Review(ReviewBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    approved: bool = False
    adminResponse: Optional[str] = None

class ReviewUpdate(BaseModel):
    approved: Optional[bool] = None
    adminResponse: Optional[str] = None

# Appointment Model
class AppointmentBase(BaseModel):
    customerName: str
    customerPhone: str
    customerEmail: Optional[EmailStr] = None
    serviceId: str
    serviceName: str
    preferredDate: str
    preferredTime: str
    motorcycleModel: Optional[str] = None
    notes: Optional[str] = None

class Appointment(AppointmentBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, confirmed, completed, cancelled

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
