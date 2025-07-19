from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ClientType(str, Enum):
    """Tipo de cliente"""
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    PREMIUM = "premium"

class ClientStatus(str, Enum):
    """Estado del cliente"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class ClientBase(BaseModel):
    """Modelo base para cliente"""
    name: str = Field(..., min_length=2, max_length=100, description="Nombre completo del cliente")
    email: EmailStr = Field(..., description="Email del cliente (único)")
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$', description="Teléfono de contacto")
    address: Optional[str] = Field(None, max_length=255, description="Dirección del cliente")
    city: Optional[str] = Field(None, max_length=50, description="Ciudad")
    country: Optional[str] = Field(None, max_length=50, description="País")
    client_type: ClientType = Field(ClientType.INDIVIDUAL, description="Tipo de cliente")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip().title()

    @validator('phone')
    def validate_phone(cls, v):
        if v and len(v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 7:
            raise ValueError('Teléfono debe tener al menos 7 dígitos')
        return v

class ClientCreate(ClientBase):
    """Modelo para crear cliente"""
    pass

class ClientUpdate(BaseModel):
    """Modelo para actualizar cliente"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    client_type: Optional[ClientType] = None
    status: Optional[ClientStatus] = None
    notes: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip().title() if v else v

class ClientResponse(ClientBase):
    """Modelo de respuesta para cliente"""
    id: int = Field(..., description="ID único del cliente")
    status: ClientStatus = Field(ClientStatus.ACTIVE, description="Estado del cliente")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    total_purchases: Optional[float] = Field(0.0, description="Total de compras realizadas")
    purchase_count: Optional[int] = Field(0, description="Número de compras realizadas")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",
                "phone": "+57 300 123 4567",
                "address": "Calle 123 #45-67",
                "city": "Bogotá",
                "country": "Colombia",
                "client_type": "individual",
                "status": "active",
                "notes": "Cliente preferencial",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-20T15:45:00",
                "total_purchases": 1500000.00,
                "purchase_count": 5
            }
        }

class ClientList(BaseModel):
    """Modelo para lista paginada de clientes"""
    clients: List[ClientResponse]
    total: int = Field(..., description="Total de clientes")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Elementos por página")
    has_next: bool = Field(..., description="Tiene página siguiente")
    has_prev: bool = Field(..., description="Tiene página anterior")

class ClientStats(BaseModel):
    """Estadísticas de clientes"""
    total_clients: int
    active_clients: int
    inactive_clients: int
    premium_clients: int
    total_revenue: float
    avg_purchase_per_client: float
