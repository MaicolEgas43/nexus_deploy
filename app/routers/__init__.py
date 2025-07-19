"""
Routers FastAPI para la aplicación Store Management API
Este módulo centraliza todos los routers organizados por funcionalidad
"""

# Importar todos los routers
from .client import router as client_router
from .product import router as product_router  
from .sales import router as sales_router

# Versión del módulo de routers
__version__ = "1.0.0"

# Lista de todos los routers disponibles
__all__ = [
    "client_router",
    "product_router", 
    "sales_router"
]

# Función de utilidad para registrar todos los routers en una app FastAPI
def include_all_routers(app):
    """
    Registra todos los routers en la aplicación FastAPI
    
    Args:
        app: Instancia de FastAPI
    """
    
    # Registrar router de clientes
    app.include_router(
        client_router,
        prefix="/api/v1",
        tags=["clients"]
    )
    
    # Registrar router de productos
    app.include_router(
        product_router,
        prefix="/api/v1", 
        tags=["products"]
    )
    
    # Registrar router de ventas
    app.include_router(
        sales_router,
        prefix="/api/v1",
        tags=["sales"] 
    )

# Metadatos de los routers para documentación
ROUTER_METADATA = {
    "client_router": {
        "name": "Clientes",
        "description": "Gestión completa de clientes con CRUD, estadísticas y búsqueda",
        "endpoints": 8,
        "prefix": "/api/v1/clients"
    },
    "product_router": {
        "name": "Productos", 
        "description": "Gestión de productos, inventario, categorías y movimientos de stock",
        "endpoints": 11,
        "prefix": "/api/v1/products"
    },
    "sales_router": {
        "name": "Ventas",
        "description": "Gestión de ventas, cálculos automáticos, reportes y reembolsos", 
        "endpoints": 10,
        "prefix": "/api/v1/sales"
    }
}

def get_router_info():
    """
    Obtiene información resumida de todos los routers
    
    Returns:
        dict: Información de routers disponibles
    """
    return {
        "total_routers": len(__all__),
        "total_endpoints": sum(meta["endpoints"] for meta in ROUTER_METADATA.values()),
        "routers": ROUTER_METADATA,
        "version": __version__
    } 