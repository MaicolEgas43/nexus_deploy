from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal

class ProductCategory(str, Enum):
    """Categorías de productos"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME = "home"
    BOOKS = "books"
    SPORTS = "sports"
    BEAUTY = "beauty"
    AUTOMOTIVE = "automotive"
    FOOD = "food"
    OTHER = "other"

class ProductStatus(str, Enum):
    """Estado del producto"""
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    PENDING = "pending"

class ProductBase(BaseModel):
    """Modelo base para producto"""
    name: str = Field(..., min_length=2, max_length=150, description="Nombre del producto")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción detallada")
    sku: Optional[str] = Field(None, max_length=50, description="Código SKU único")
    category: ProductCategory = Field(..., description="Categoría del producto")
    price: float = Field(..., gt=0, description="Precio unitario del producto")
    cost: Optional[float] = Field(None, ge=0, description="Costo del producto")
    stock_quantity: int = Field(0, ge=0, description="Cantidad en inventario")
    min_stock: int = Field(0, ge=0, description="Stock mínimo para alertas")
    weight: Optional[float] = Field(None, gt=0, description="Peso en kg")
    dimensions: Optional[str] = Field(None, max_length=100, description="Dimensiones (LxWxH)")
    brand: Optional[str] = Field(None, max_length=100, description="Marca del producto")
    model: Optional[str] = Field(None, max_length=100, description="Modelo del producto")
    warranty_months: Optional[int] = Field(None, ge=0, le=120, description="Garantía en meses")
    tags: Optional[List[str]] = Field(None, description="Etiquetas para búsqueda")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('El nombre del producto no puede estar vacío')
        return v.strip().title()

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return round(v, 2)

    @validator('cost')
    def validate_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError('El costo no puede ser negativo')
        return round(v, 2) if v else v

    @validator('sku')
    def validate_sku(cls, v):
        if v:
            return v.upper().strip()
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Limitar a 10 tags máximo
            if len(v) > 10:
                raise ValueError('Máximo 10 etiquetas permitidas')
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v

class ProductCreate(ProductBase):
    """Modelo para crear producto"""
    pass

class ProductUpdate(BaseModel):
    """Modelo para actualizar producto"""
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    sku: Optional[str] = Field(None, max_length=50)
    category: Optional[ProductCategory] = None
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    warranty_months: Optional[int] = Field(None, ge=0, le=120)
    status: Optional[ProductStatus] = None
    tags: Optional[List[str]] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('El nombre del producto no puede estar vacío')
        return v.strip().title() if v else v

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return round(v, 2) if v else v

class ProductResponse(ProductBase):
    """Modelo de respuesta para producto"""
    id: int = Field(..., description="ID único del producto")
    status: ProductStatus = Field(ProductStatus.AVAILABLE, description="Estado del producto")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    total_sold: int = Field(0, description="Cantidad total vendida")
    revenue: float = Field(0.0, description="Ingresos generados por el producto")
    profit_margin: Optional[float] = Field(None, description="Margen de ganancia (%)")
    is_low_stock: bool = Field(False, description="Indica si el stock está bajo")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Smartphone Samsung Galaxy",
                "description": "Smartphone con pantalla AMOLED de 6.5 pulgadas",
                "sku": "SAMS-GALAXY-001",
                "category": "electronics",
                "price": 899999.99,
                "cost": 600000.00,
                "stock_quantity": 25,
                "min_stock": 5,
                "weight": 0.175,
                "dimensions": "15.1 x 7.2 x 0.8 cm",
                "brand": "Samsung",
                "model": "Galaxy S24",
                "warranty_months": 12,
                "tags": ["smartphone", "android", "5g"],
                "status": "available",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-20T15:45:00",
                "total_sold": 150,
                "revenue": 134999998.50,
                "profit_margin": 33.33,
                "is_low_stock": False
            }
        }

class ProductList(BaseModel):
    """Modelo para lista paginada de productos"""
    products: List[ProductResponse]
    total: int = Field(..., description="Total de productos")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Elementos por página")
    has_next: bool = Field(..., description="Tiene página siguiente")
    has_prev: bool = Field(..., description="Tiene página anterior")

class ProductStats(BaseModel):
    """Estadísticas de productos"""
    total_products: int
    available_products: int
    out_of_stock_products: int
    low_stock_products: int
    total_inventory_value: float
    avg_price: float
    top_category: str
    total_revenue: float

class StockMovement(BaseModel):
    """Movimiento de inventario"""
    product_id: int
    movement_type: str = Field(..., pattern="^(in|out|adjustment)$")
    quantity: int = Field(..., description="Cantidad (positiva o negativa)")
    reason: str = Field(..., max_length=200, description="Razón del movimiento")
    reference: Optional[str] = Field(None, max_length=100, description="Referencia externa")
    created_at: datetime = Field(default_factory=datetime.now)

class ProductSearch(BaseModel):
    """Filtros para búsqueda de productos"""
    name: Optional[str] = None
    category: Optional[ProductCategory] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    brand: Optional[str] = None
    status: Optional[ProductStatus] = None
    low_stock_only: Optional[bool] = False
    tags: Optional[List[str]] = None
