"""
Router para gestión de productos
Incluye endpoints CRUD, inventario, categorías, búsqueda avanzada y movimientos de stock
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from datetime import datetime
import logging

# Importar modelos desde el paquete local
from ..models.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductList,
    ProductStats,
    ProductCategory,
    ProductStatus,
    ProductSearch,
    StockMovement
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router con prefix y tags para documentación
router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={
        404: {"description": "Producto no encontrado"},
        422: {"description": "Error de validación"},
        500: {"description": "Error interno del servidor"}
    }
)

# Dependencia para paginación
def get_pagination_params(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página")
):
    """Parámetros de paginación estándar"""
    return {"page": page, "per_page": per_page}

# Dependencia para filtros de búsqueda de productos
def get_product_filters(
    name: Optional[str] = Query(None, description="Filtrar por nombre"),
    category: Optional[ProductCategory] = Query(None, description="Filtrar por categoría"),
    status: Optional[ProductStatus] = Query(None, description="Filtrar por estado"),
    brand: Optional[str] = Query(None, description="Filtrar por marca"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    sku: Optional[str] = Query(None, description="Filtrar por SKU"),
    low_stock_only: Optional[bool] = Query(False, description="Solo productos con stock bajo")
):
    """Filtros de búsqueda para productos"""
    return {
        "name": name,
        "category": category,
        "status": status,
        "brand": brand,
        "min_price": min_price,
        "max_price": max_price,
        "sku": sku,
        "low_stock_only": low_stock_only
    }

@router.get("/", response_model=ProductList, summary="Listar productos")
async def list_products(
    pagination: dict = Depends(get_pagination_params),
    filters: dict = Depends(get_product_filters)
):
    """
    Listar productos con paginación y filtros opcionales
    
    - **page**: Número de página (mínimo 1)
    - **per_page**: Elementos por página (1-100)
    - **name**: Filtrar por nombre (búsqueda parcial)
    - **category**: Filtrar por categoría
    - **status**: Filtrar por estado
    - **brand**: Filtrar por marca
    - **min_price/max_price**: Rango de precios
    - **sku**: Filtrar por SKU exacto
    - **low_stock_only**: Solo productos con stock bajo
    """
    try:
        logger.info(f"Listando productos - Página {pagination['page']}, Filtros: {filters}")
        
        # TODO: Implementar consulta real a base de datos
        # Simulación de datos para desarrollo
        mock_products = [
            ProductResponse(
                id=1,
                name="Smartphone Samsung Galaxy",
                description="Smartphone con pantalla AMOLED de 6.5 pulgadas",
                sku="SAMS-GALAXY-001",
                category=ProductCategory.ELECTRONICS,
                price=899999.99,
                cost=600000.00,
                stock_quantity=25,
                min_stock=5,
                weight=0.175,
                dimensions="15.1 x 7.2 x 0.8 cm",
                brand="Samsung",
                model="Galaxy S24",
                warranty_months=12,
                tags=["smartphone", "android", "5g"],
                status=ProductStatus.AVAILABLE,
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 20, 15, 45),
                total_sold=150,
                revenue=134999998.50,
                profit_margin=33.33,
                is_low_stock=False
            ),
            ProductResponse(
                id=2,
                name="Camiseta Algodón Premium",
                description="Camiseta 100% algodón orgánico",
                sku="ROPA-CAM-001",
                category=ProductCategory.CLOTHING,
                price=45000.00,
                cost=20000.00,
                stock_quantity=3,
                min_stock=10,
                weight=0.200,
                dimensions="L: 70cm, A: 50cm",
                brand="EcoFashion",
                model="Premium Basic",
                warranty_months=None,
                tags=["camiseta", "algodón", "premium"],
                status=ProductStatus.AVAILABLE,
                created_at=datetime(2024, 1, 10, 8, 15),
                updated_at=datetime(2024, 1, 25, 12, 30),
                total_sold=85,
                revenue=3825000.00,
                profit_margin=55.56,
                is_low_stock=True
            )
        ]
        
        # Aplicar filtros básicos (simulación)
        filtered_products = mock_products
        if filters.get("name"):
            filtered_products = [p for p in filtered_products if filters["name"].lower() in p.name.lower()]
        if filters.get("category"):
            filtered_products = [p for p in filtered_products if p.category == filters["category"]]
        if filters.get("status"):
            filtered_products = [p for p in filtered_products if p.status == filters["status"]]
        if filters.get("brand"):
            filtered_products = [p for p in filtered_products if p.brand and filters["brand"].lower() in p.brand.lower()]
        if filters.get("min_price"):
            filtered_products = [p for p in filtered_products if p.price >= filters["min_price"]]
        if filters.get("max_price"):
            filtered_products = [p for p in filtered_products if p.price <= filters["max_price"]]
        if filters.get("low_stock_only"):
            filtered_products = [p for p in filtered_products if p.is_low_stock]
            
        # Paginación simulada
        total = len(filtered_products)
        start_idx = (pagination["page"] - 1) * pagination["per_page"]
        end_idx = start_idx + pagination["per_page"]
        paginated_products = filtered_products[start_idx:end_idx]
        
        return ProductList(
            products=paginated_products,
            total=total,
            page=pagination["page"],
            per_page=pagination["per_page"],
            has_next=end_idx < total,
            has_prev=pagination["page"] > 1
        )
        
    except Exception as e:
        logger.error(f"Error listando productos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar productos"
        )

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Crear producto")
async def create_product(product: ProductCreate):
    """
    Crear un nuevo producto
    
    - **name**: Nombre del producto (requerido, 2-150 caracteres)
    - **category**: Categoría del producto (requerido)
    - **price**: Precio unitario (requerido, mayor a 0)
    - **description**: Descripción detallada (opcional)
    - **sku**: Código SKU único (opcional)
    - **cost**: Costo del producto (opcional)
    - **stock_quantity**: Cantidad inicial en inventario
    - **min_stock**: Stock mínimo para alertas
    - Campos adicionales: weight, dimensions, brand, model, warranty_months, tags
    """
    try:
        logger.info(f"Creando producto: {product.name}")
        
        # TODO: Validar SKU único en base de datos
        # TODO: Implementar creación real en base de datos
        
        # Simulación de creación
        new_product = ProductResponse(
            id=999,  # ID generado por la base de datos
            **product.dict(),
            status=ProductStatus.AVAILABLE,
            created_at=datetime.now(),
            updated_at=None,
            total_sold=0,
            revenue=0.0,
            profit_margin=((product.price - (product.cost or 0)) / product.price * 100) if product.cost else None,
            is_low_stock=product.stock_quantity <= product.min_stock
        )
        
        logger.info(f"Producto creado exitosamente: ID {new_product.id}")
        return new_product
        
    except ValueError as e:
        logger.warning(f"Error de validación creando producto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear producto"
        )

@router.get("/{product_id}", response_model=ProductResponse, summary="Obtener producto")
async def get_product(product_id: int):
    """
    Obtener un producto específico por ID
    
    - **product_id**: ID único del producto
    """
    try:
        logger.info(f"Obteniendo producto ID: {product_id}")
        
        # TODO: Implementar consulta real a base de datos
        if product_id == 1:
            return ProductResponse(
                id=1,
                name="Smartphone Samsung Galaxy",
                description="Smartphone con pantalla AMOLED de 6.5 pulgadas",
                sku="SAMS-GALAXY-001",
                category=ProductCategory.ELECTRONICS,
                price=899999.99,
                cost=600000.00,
                stock_quantity=25,
                min_stock=5,
                weight=0.175,
                dimensions="15.1 x 7.2 x 0.8 cm",
                brand="Samsung",
                model="Galaxy S24",
                warranty_months=12,
                tags=["smartphone", "android", "5g"],
                status=ProductStatus.AVAILABLE,
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 20, 15, 45),
                total_sold=150,
                revenue=134999998.50,
                profit_margin=33.33,
                is_low_stock=False
            )
        
        logger.warning(f"Producto no encontrado: ID {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener producto"
        )

@router.put("/{product_id}", response_model=ProductResponse, summary="Actualizar producto")
async def update_product(product_id: int, product_update: ProductUpdate):
    """
    Actualizar un producto existente
    
    - **product_id**: ID único del producto
    - Solo se actualizan los campos proporcionados
    """
    try:
        logger.info(f"Actualizando producto ID: {product_id}")
        
        # TODO: Verificar que el producto existe
        # TODO: Implementar actualización real en base de datos
        
        if product_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        # Simular producto actualizado
        updated_product = ProductResponse(
            id=product_id,
            name=product_update.name or "Smartphone Samsung Galaxy",
            description=product_update.description or "Smartphone con pantalla AMOLED de 6.5 pulgadas",
            sku=product_update.sku or "SAMS-GALAXY-001",
            category=product_update.category or ProductCategory.ELECTRONICS,
            price=product_update.price or 899999.99,
            cost=product_update.cost or 600000.00,
            stock_quantity=product_update.stock_quantity or 25,
            min_stock=product_update.min_stock or 5,
            weight=product_update.weight or 0.175,
            dimensions=product_update.dimensions or "15.1 x 7.2 x 0.8 cm",
            brand=product_update.brand or "Samsung",
            model=product_update.model or "Galaxy S24",
            warranty_months=product_update.warranty_months or 12,
            tags=product_update.tags or ["smartphone", "android", "5g"],
            status=product_update.status or ProductStatus.AVAILABLE,
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime.now(),
            total_sold=150,
            revenue=134999998.50,
            profit_margin=33.33,
            is_low_stock=False
        )
        
        logger.info(f"Producto actualizado exitosamente: ID {product_id}")
        return updated_product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar producto"
        )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar producto")
async def delete_product(product_id: int):
    """
    Eliminar un producto
    
    - **product_id**: ID único del producto
    - **Nota**: Eliminación lógica (cambiar status a discontinued)
    """
    try:
        logger.info(f"Eliminando producto ID: {product_id}")
        
        # TODO: Verificar que el producto existe
        # TODO: Verificar que no tenga ventas pendientes
        # TODO: Implementar eliminación lógica en base de datos
        
        if product_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        logger.info(f"Producto eliminado exitosamente: ID {product_id}")
        return  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al eliminar producto"
        )

@router.get("/categories/list", summary="Listar categorías")
async def list_categories():
    """
    Obtener lista de todas las categorías disponibles
    """
    try:
        categories = [
            {"value": category.value, "label": category.value.replace("_", " ").title()}
            for category in ProductCategory
        ]
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener categorías"
        )

@router.get("/stats/overview", response_model=ProductStats, summary="Estadísticas de productos")
async def get_product_stats():
    """
    Obtener estadísticas generales de productos
    
    Incluye:
    - Total de productos por estado
    - Productos con stock bajo
    - Valor total del inventario
    - Precio promedio
    - Categoría más popular
    - Ingresos totales
    """
    try:
        logger.info("Obteniendo estadísticas de productos")
        
        # TODO: Implementar consultas reales a base de datos
        stats = ProductStats(
            total_products=250,
            available_products=220,
            out_of_stock_products=15,
            low_stock_products=25,
            total_inventory_value=125000000.00,
            avg_price=350000.00,
            top_category="electronics",
            total_revenue=85000000.00
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de productos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estadísticas"
        )

@router.get("/low-stock", response_model=ProductList, summary="Productos con stock bajo")
async def get_low_stock_products(
    pagination: dict = Depends(get_pagination_params)
):
    """
    Obtener productos con stock bajo (stock_quantity <= min_stock)
    
    - Incluye paginación estándar
    """
    try:
        logger.info("Obteniendo productos con stock bajo")
        
        # TODO: Implementar consulta real a base de datos
        # Usar el filtro low_stock_only=True
        return await list_products(
            pagination=pagination,
            filters={"low_stock_only": True}
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo productos con stock bajo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener productos con stock bajo"
        )

@router.post("/{product_id}/stock", summary="Actualizar stock")
async def update_stock(
    product_id: int,
    movement: StockMovement
):
    """
    Registrar movimiento de inventario
    
    - **product_id**: ID del producto
    - **movement_type**: Tipo de movimiento (in/out/adjustment)
    - **quantity**: Cantidad (positiva para entrada, negativa para salida)
    - **reason**: Razón del movimiento
    - **reference**: Referencia externa opcional
    """
    try:
        logger.info(f"Actualizando stock del producto ID: {product_id}")
        
        # TODO: Verificar que el producto existe
        # TODO: Validar cantidad disponible para movimientos de salida
        # TODO: Implementar actualización real de stock en base de datos
        # TODO: Registrar movimiento en tabla de auditoría
        
        if product_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        return {
            "message": "Stock actualizado exitosamente",
            "product_id": product_id,
            "movement": movement.dict(),
            "new_stock": 30  # Nuevo stock simulado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando stock del producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar stock"
        )

@router.get("/{product_id}/stock-history", summary="Historial de movimientos")
async def get_stock_history(
    product_id: int,
    pagination: dict = Depends(get_pagination_params)
):
    """
    Obtener historial de movimientos de stock de un producto
    
    - **product_id**: ID único del producto
    - Incluye paginación estándar
    """
    try:
        logger.info(f"Obteniendo historial de stock del producto ID: {product_id}")
        
        # TODO: Verificar que el producto existe
        # TODO: Implementar consulta real de movimientos
        
        if product_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        # Simulación de historial
        return {
            "product_id": product_id,
            "movements": [],  # Lista de movimientos
            "total_movements": 0,
            "current_stock": 25,
            "page": pagination["page"],
            "per_page": pagination["per_page"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo historial de stock del producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener historial de stock"
        )
