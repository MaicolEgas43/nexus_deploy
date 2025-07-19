from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from decimal import Decimal

class PaymentMethod(str, Enum):
    """Métodos de pago"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    DIGITAL_WALLET = "digital_wallet"
    STORE_CREDIT = "store_credit"

class SaleStatus(str, Enum):
    """Estados de la venta"""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class SaleItemBase(BaseModel):
    """Modelo base para items de venta"""
    product_id: int = Field(..., description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad vendida")
    unit_price: float = Field(..., gt=0, description="Precio unitario en el momento de la venta")
    discount_percentage: float = Field(0.0, ge=0, le=100, description="Descuento aplicado (%)")

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')
        return v

    @validator('unit_price')
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('El precio unitario debe ser mayor a 0')
        return round(v, 2)

    @validator('discount_percentage')
    def validate_discount(cls, v):
        if v < 0 or v > 100:
            raise ValueError('El descuento debe estar entre 0 y 100%')
        return round(v, 2)

class SaleItemCreate(SaleItemBase):
    """Modelo para crear item de venta"""
    pass

class SaleItemResponse(SaleItemBase):
    """Modelo de respuesta para item de venta"""
    id: int = Field(..., description="ID del item")
    product_name: str = Field(..., description="Nombre del producto")
    product_sku: Optional[str] = Field(None, description="SKU del producto")
    subtotal: float = Field(..., description="Subtotal del item (quantity * unit_price)")
    discount_amount: float = Field(..., description="Monto del descuento")
    line_total: float = Field(..., description="Total de la línea después del descuento")

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    """Modelo base para venta"""
    client_id: int = Field(..., description="ID del cliente")
    sale_date: datetime = Field(default_factory=datetime.now, description="Fecha de la venta")
    payment_method: PaymentMethod = Field(..., description="Método de pago")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    discount_percentage: float = Field(0.0, ge=0, le=100, description="Descuento general (%)")
    tax_percentage: float = Field(19.0, ge=0, le=100, description="Porcentaje de impuestos")
    shipping_cost: float = Field(0.0, ge=0, description="Costo de envío")
    items: List[SaleItemCreate] = Field(..., min_items=1, description="Items de la venta")

    @validator('discount_percentage')
    def validate_discount(cls, v):
        if v < 0 or v > 100:
            raise ValueError('El descuento debe estar entre 0 y 100%')
        return round(v, 2)

    @validator('tax_percentage')
    def validate_tax(cls, v):
        if v < 0 or v > 100:
            raise ValueError('El impuesto debe estar entre 0 y 100%')
        return round(v, 2)

    @validator('shipping_cost')
    def validate_shipping(cls, v):
        if v < 0:
            raise ValueError('El costo de envío no puede ser negativo')
        return round(v, 2)

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('La venta debe tener al menos un item')
        
        # Verificar que no haya productos duplicados
        product_ids = [item.product_id for item in v]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError('No se pueden duplicar productos en la misma venta')
        
        return v

class SaleCreate(SaleBase):
    """Modelo para crear venta"""
    pass

class SaleUpdate(BaseModel):
    """Modelo para actualizar venta"""
    client_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = Field(None, max_length=500)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    tax_percentage: Optional[float] = Field(None, ge=0, le=100)
    shipping_cost: Optional[float] = Field(None, ge=0)
    status: Optional[SaleStatus] = None

class SaleResponse(BaseModel):
    """Modelo de respuesta para venta"""
    id: int = Field(..., description="ID único de la venta")
    sale_number: str = Field(..., description="Número de venta generado")
    client_id: int = Field(..., description="ID del cliente")
    client_name: str = Field(..., description="Nombre del cliente")
    client_email: str = Field(..., description="Email del cliente")
    sale_date: datetime = Field(..., description="Fecha de la venta")
    payment_method: PaymentMethod = Field(..., description="Método de pago")
    status: SaleStatus = Field(SaleStatus.PENDING, description="Estado de la venta")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    
    # Cálculos automáticos
    subtotal: float = Field(..., description="Subtotal de todos los items")
    discount_percentage: float = Field(..., description="Descuento general (%)")
    discount_amount: float = Field(..., description="Monto total del descuento")
    tax_percentage: float = Field(..., description="Porcentaje de impuestos")
    tax_amount: float = Field(..., description="Monto de impuestos")
    shipping_cost: float = Field(..., description="Costo de envío")
    total_amount: float = Field(..., description="Total final de la venta")
    
    # Información adicional
    items_count: int = Field(..., description="Número de items diferentes")
    total_items: int = Field(..., description="Cantidad total de productos")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    # Items de la venta
    items: List[SaleItemResponse] = Field(..., description="Items de la venta")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "sale_number": "VEN-2024-001",
                "client_id": 1,
                "client_name": "Juan Pérez",
                "client_email": "juan.perez@example.com",
                "sale_date": "2024-01-15T14:30:00",
                "payment_method": "credit_card",
                "status": "paid",
                "notes": "Entrega express solicitada",
                "subtotal": 1500000.00,
                "discount_percentage": 10.0,
                "discount_amount": 150000.00,
                "tax_percentage": 19.0,
                "tax_amount": 256500.00,
                "shipping_cost": 25000.00,
                "total_amount": 1631500.00,
                "items_count": 2,
                "total_items": 3,
                "created_at": "2024-01-15T14:30:00",
                "updated_at": "2024-01-15T15:00:00",
                "items": []
            }
        }

class SaleList(BaseModel):
    """Modelo para lista paginada de ventas"""
    sales: List[SaleResponse]
    total: int = Field(..., description="Total de ventas")
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Elementos por página")
    has_next: bool = Field(..., description="Tiene página siguiente")
    has_prev: bool = Field(..., description="Tiene página anterior")
    total_amount: float = Field(..., description="Suma total de ventas")

class SaleStats(BaseModel):
    """Estadísticas de ventas"""
    total_sales: int
    total_revenue: float
    avg_sale_amount: float
    today_sales: int
    today_revenue: float
    monthly_sales: int
    monthly_revenue: float
    top_payment_method: str
    pending_sales: int
    completed_sales: int

class SalesReport(BaseModel):
    """Reporte de ventas por período"""
    start_date: date
    end_date: date
    total_sales: int
    total_revenue: float
    total_items_sold: int
    avg_sale_amount: float
    sales_by_status: dict
    sales_by_payment_method: dict
    sales_by_day: List[dict]
    top_products: List[dict]
    top_clients: List[dict]

class SaleSearch(BaseModel):
    """Filtros para búsqueda de ventas"""
    client_id: Optional[int] = None
    status: Optional[SaleStatus] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    sale_number: Optional[str] = None

    @model_validator(mode='after')
    def validate_date_range(self):
        start_date = self.start_date
        end_date = self.end_date
        
        if start_date and end_date and start_date > end_date:
            raise ValueError('La fecha de inicio debe ser anterior a la fecha de fin')
        
        return self

    @model_validator(mode='after')
    def validate_amount_range(self):
        min_amount = self.min_amount
        max_amount = self.max_amount
        
        if min_amount is not None and max_amount is not None and min_amount > max_amount:
            raise ValueError('El monto mínimo debe ser menor al monto máximo')
        
        return self

class RefundRequest(BaseModel):
    """Solicitud de reembolso"""
    sale_id: int = Field(..., description="ID de la venta a reembolsar")
    reason: str = Field(..., min_length=10, max_length=500, description="Razón del reembolso")
    amount: Optional[float] = Field(None, gt=0, description="Monto a reembolsar (vacío = total)")
    refund_shipping: bool = Field(False, description="Incluir costo de envío en reembolso")
    
    @validator('reason')
    def validate_reason(cls, v):
        if not v.strip():
            raise ValueError('La razón del reembolso no puede estar vacía')
        return v.strip()
