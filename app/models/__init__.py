"""
Modelos Pydantic para la aplicación Store Management API
Este módulo exporta todos los modelos necesarios para la validación de datos
"""

# Importar modelos de clientes
from .client import (
    ClientType,
    ClientStatus,
    ClientBase,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientList,
    ClientStats
)

# Importar modelos de productos
from .product import (
    ProductCategory,
    ProductStatus,
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductList,
    ProductStats,
    StockMovement,
    ProductSearch
)

# Importar modelos de ventas
from .sales import (
    PaymentMethod,
    SaleStatus,
    SaleItemBase,
    SaleItemCreate,
    SaleItemResponse,
    SaleBase,
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SaleList,
    SaleStats,
    SalesReport,
    SaleSearch,
    RefundRequest
)

# Versión del módulo de modelos
__version__ = "1.0.0"

# Lista de todos los modelos disponibles para validación
__all__ = [
    # Clientes
    "ClientType",
    "ClientStatus", 
    "ClientBase",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientList",
    "ClientStats",
    
    # Productos
    "ProductCategory",
    "ProductStatus",
    "ProductBase",
    "ProductCreate", 
    "ProductUpdate",
    "ProductResponse",
    "ProductList",
    "ProductStats",
    "StockMovement",
    "ProductSearch",
    
    # Ventas
    "PaymentMethod",
    "SaleStatus",
    "SaleItemBase",
    "SaleItemCreate",
    "SaleItemResponse", 
    "SaleBase",
    "SaleCreate",
    "SaleUpdate",
    "SaleResponse",
    "SaleList",
    "SaleStats",
    "SalesReport",
    "SaleSearch",
    "RefundRequest"
] 