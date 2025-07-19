"""
Router para gestión de ventas
Incluye endpoints CRUD, relaciones cliente-producto, cálculos automáticos, reportes y reembolsos
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from datetime import datetime, date, timedelta
import logging

# Importar modelos desde el paquete local
from ..models.sales import (
    SaleCreate,
    SaleUpdate,
    SaleResponse,
    SaleList,
    SaleStats,
    SalesReport,
    SaleSearch,
    PaymentMethod,
    SaleStatus,
    RefundRequest
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router con prefix y tags para documentación
router = APIRouter(
    prefix="/sales",
    tags=["sales"],
    responses={
        404: {"description": "Venta no encontrada"},
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

# Dependencia para filtros de búsqueda de ventas
def get_sale_filters(
    client_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    status: Optional[SaleStatus] = Query(None, description="Filtrar por estado"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filtrar por método de pago"),
    start_date: Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    min_amount: Optional[float] = Query(None, ge=0, description="Monto mínimo"),
    max_amount: Optional[float] = Query(None, ge=0, description="Monto máximo"),
    sale_number: Optional[str] = Query(None, description="Número de venta")
):
    """Filtros de búsqueda para ventas"""
    return {
        "client_id": client_id,
        "status": status,
        "payment_method": payment_method,
        "start_date": start_date,
        "end_date": end_date,
        "min_amount": min_amount,
        "max_amount": max_amount,
        "sale_number": sale_number
    }

@router.get("/", response_model=SaleList, summary="Listar ventas")
async def list_sales(
    pagination: dict = Depends(get_pagination_params),
    filters: dict = Depends(get_sale_filters)
):
    """
    Listar ventas con paginación y filtros opcionales
    
    - **page**: Número de página (mínimo 1)
    - **per_page**: Elementos por página (1-100)
    - **client_id**: Filtrar por ID de cliente
    - **status**: Filtrar por estado de la venta
    - **payment_method**: Filtrar por método de pago
    - **start_date/end_date**: Rango de fechas
    - **min_amount/max_amount**: Rango de montos
    - **sale_number**: Buscar por número de venta
    """
    try:
        logger.info(f"Listando ventas - Página {pagination['page']}, Filtros: {filters}")
        
        # TODO: Implementar consulta real a base de datos
        # Simulación de datos para desarrollo
        mock_sales = [
            SaleResponse(
                id=1,
                sale_number="VEN-2024-001",
                client_id=1,
                client_name="Juan Pérez",
                client_email="juan.perez@example.com",
                sale_date=datetime(2024, 1, 15, 14, 30),
                payment_method=PaymentMethod.CREDIT_CARD,
                status=SaleStatus.PAID,
                notes="Entrega express solicitada",
                subtotal=1500000.00,
                discount_percentage=10.0,
                discount_amount=150000.00,
                tax_percentage=19.0,
                tax_amount=256500.00,
                shipping_cost=25000.00,
                total_amount=1631500.00,
                items_count=2,
                total_items=3,
                created_at=datetime(2024, 1, 15, 14, 30),
                updated_at=datetime(2024, 1, 15, 15, 0),
                items=[]
            ),
            SaleResponse(
                id=2,
                sale_number="VEN-2024-002",
                client_id=2,
                client_name="Empresa ABC S.A.S.",
                client_email="contacto@empresaabc.com",
                sale_date=datetime(2024, 1, 20, 10, 15),
                payment_method=PaymentMethod.BANK_TRANSFER,
                status=SaleStatus.CONFIRMED,
                notes="Facturación corporativa",
                subtotal=3000000.00,
                discount_percentage=5.0,
                discount_amount=150000.00,
                tax_percentage=19.0,
                tax_amount=541500.00,
                shipping_cost=50000.00,
                total_amount=3441500.00,
                items_count=4,
                total_items=8,
                created_at=datetime(2024, 1, 20, 10, 15),
                updated_at=datetime(2024, 1, 20, 11, 30),
                items=[]
            )
        ]
        
        # Aplicar filtros básicos (simulación)
        filtered_sales = mock_sales
        if filters.get("client_id"):
            filtered_sales = [s for s in filtered_sales if s.client_id == filters["client_id"]]
        if filters.get("status"):
            filtered_sales = [s for s in filtered_sales if s.status == filters["status"]]
        if filters.get("payment_method"):
            filtered_sales = [s for s in filtered_sales if s.payment_method == filters["payment_method"]]
        if filters.get("min_amount"):
            filtered_sales = [s for s in filtered_sales if s.total_amount >= filters["min_amount"]]
        if filters.get("max_amount"):
            filtered_sales = [s for s in filtered_sales if s.total_amount <= filters["max_amount"]]
        if filters.get("sale_number"):
            filtered_sales = [s for s in filtered_sales if filters["sale_number"] in s.sale_number]
            
        # Paginación simulada
        total = len(filtered_sales)
        start_idx = (pagination["page"] - 1) * pagination["per_page"]
        end_idx = start_idx + pagination["per_page"]
        paginated_sales = filtered_sales[start_idx:end_idx]
        
        # Calcular total amount de las ventas filtradas
        total_amount = sum(sale.total_amount for sale in filtered_sales)
        
        return SaleList(
            sales=paginated_sales,
            total=total,
            page=pagination["page"],
            per_page=pagination["per_page"],
            has_next=end_idx < total,
            has_prev=pagination["page"] > 1,
            total_amount=total_amount
        )
        
    except Exception as e:
        logger.error(f"Error listando ventas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar ventas"
        )

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED, summary="Crear venta")
async def create_sale(sale: SaleCreate):
    """
    Crear una nueva venta
    
    - **client_id**: ID del cliente (requerido)
    - **payment_method**: Método de pago (requerido)
    - **items**: Lista de items con product_id, quantity, unit_price
    - **notes**: Notas adicionales (opcional)
    - **discount_percentage**: Descuento general (0-100%)
    - **tax_percentage**: Porcentaje de impuestos (default 19%)
    - **shipping_cost**: Costo de envío (default 0)
    
    Los cálculos se realizan automáticamente:
    - Subtotal = suma de (quantity * unit_price) de todos los items
    - Descuentos por item y descuento general
    - Impuestos aplicados después de descuentos
    - Total final = subtotal - descuentos + impuestos + envío
    """
    try:
        logger.info(f"Creando venta para cliente: {sale.client_id}")
        
        # TODO: Verificar que el cliente existe
        # TODO: Verificar que todos los productos existen y tienen stock suficiente
        # TODO: Implementar cálculos reales y creación en base de datos
        
        # Simulación de cálculos automáticos
        subtotal = sum(item.quantity * item.unit_price for item in sale.items)
        discount_amount = subtotal * (sale.discount_percentage / 100)
        after_discount = subtotal - discount_amount
        tax_amount = after_discount * (sale.tax_percentage / 100)
        total_amount = after_discount + tax_amount + sale.shipping_cost
        
        # Generar número de venta
        sale_number = f"VEN-2024-{999:03d}"
        
        # Simulación de venta creada
        new_sale = SaleResponse(
            id=999,  # ID generado por la base de datos
            sale_number=sale_number,
            client_id=sale.client_id,
            client_name="Cliente Simulado",  # Obtener del cliente real
            client_email="cliente@example.com",  # Obtener del cliente real
            sale_date=sale.sale_date,
            payment_method=sale.payment_method,
            status=SaleStatus.PENDING,
            notes=sale.notes,
            subtotal=subtotal,
            discount_percentage=sale.discount_percentage,
            discount_amount=discount_amount,
            tax_percentage=sale.tax_percentage,
            tax_amount=tax_amount,
            shipping_cost=sale.shipping_cost,
            total_amount=total_amount,
            items_count=len(sale.items),
            total_items=sum(item.quantity for item in sale.items),
            created_at=datetime.now(),
            updated_at=None,
            items=[]  # Se poblaría con los items creados
        )
        
        logger.info(f"Venta creada exitosamente: {sale_number}")
        return new_sale
        
    except ValueError as e:
        logger.warning(f"Error de validación creando venta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando venta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear venta"
        )

@router.get("/{sale_id}", response_model=SaleResponse, summary="Obtener venta")
async def get_sale(sale_id: int):
    """
    Obtener una venta específica por ID
    
    - **sale_id**: ID único de la venta
    - Incluye todos los items de la venta con detalles del producto
    """
    try:
        logger.info(f"Obteniendo venta ID: {sale_id}")
        
        # TODO: Implementar consulta real a base de datos
        if sale_id == 1:
            return SaleResponse(
                id=1,
                sale_number="VEN-2024-001",
                client_id=1,
                client_name="Juan Pérez",
                client_email="juan.perez@example.com",
                sale_date=datetime(2024, 1, 15, 14, 30),
                payment_method=PaymentMethod.CREDIT_CARD,
                status=SaleStatus.PAID,
                notes="Entrega express solicitada",
                subtotal=1500000.00,
                discount_percentage=10.0,
                discount_amount=150000.00,
                tax_percentage=19.0,
                tax_amount=256500.00,
                shipping_cost=25000.00,
                total_amount=1631500.00,
                items_count=2,
                total_items=3,
                created_at=datetime(2024, 1, 15, 14, 30),
                updated_at=datetime(2024, 1, 15, 15, 0),
                items=[]  # Items con detalles completos
            )
        
        logger.warning(f"Venta no encontrada: ID {sale_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venta con ID {sale_id} no encontrada"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo venta {sale_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener venta"
        )

@router.put("/{sale_id}", response_model=SaleResponse, summary="Actualizar venta")
async def update_sale(sale_id: int, sale_update: SaleUpdate):
    """
    Actualizar una venta existente
    
    - **sale_id**: ID único de la venta
    - Solo se actualizan los campos proporcionados
    - **Restricciones**: No se pueden modificar ventas pagadas o entregadas
    """
    try:
        logger.info(f"Actualizando venta ID: {sale_id}")
        
        # TODO: Verificar que la venta existe
        # TODO: Verificar estado para permitir modificaciones
        # TODO: Recalcular totales si se modifican descuentos o envío
        # TODO: Implementar actualización real en base de datos
        
        if sale_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {sale_id} no encontrada"
            )
        
        # Verificar si la venta puede ser modificada
        current_status = SaleStatus.PAID  # Obtener del BD
        if current_status in [SaleStatus.PAID, SaleStatus.DELIVERED, SaleStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede modificar una venta en estado {current_status.value}"
            )
        
        # Simular venta actualizada
        updated_sale = SaleResponse(
            id=sale_id,
            sale_number="VEN-2024-001",
            client_id=sale_update.client_id or 1,
            client_name="Juan Pérez",
            client_email="juan.perez@example.com",
            sale_date=datetime(2024, 1, 15, 14, 30),
            payment_method=sale_update.payment_method or PaymentMethod.CREDIT_CARD,
            status=sale_update.status or SaleStatus.PENDING,
            notes=sale_update.notes or "Entrega express solicitada",
            subtotal=1500000.00,
            discount_percentage=sale_update.discount_percentage or 10.0,
            discount_amount=150000.00,
            tax_percentage=sale_update.tax_percentage or 19.0,
            tax_amount=256500.00,
            shipping_cost=sale_update.shipping_cost or 25000.00,
            total_amount=1631500.00,
            items_count=2,
            total_items=3,
            created_at=datetime(2024, 1, 15, 14, 30),
            updated_at=datetime.now(),
            items=[]
        )
        
        logger.info(f"Venta actualizada exitosamente: ID {sale_id}")
        return updated_sale
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando venta {sale_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar venta"
        )

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Cancelar venta")
async def cancel_sale(sale_id: int):
    """
    Cancelar una venta (eliminación lógica)
    
    - **sale_id**: ID único de la venta
    - **Nota**: Cambia el status a cancelled, no elimina físicamente
    - **Restricciones**: No se pueden cancelar ventas pagadas o entregadas
    """
    try:
        logger.info(f"Cancelando venta ID: {sale_id}")
        
        # TODO: Verificar que la venta existe
        # TODO: Verificar estado para permitir cancelación
        # TODO: Restaurar stock de productos si es necesario
        # TODO: Implementar cancelación en base de datos
        
        if sale_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {sale_id} no encontrada"
            )
        
        # Verificar si la venta puede ser cancelada
        current_status = SaleStatus.PENDING  # Obtener del BD
        if current_status in [SaleStatus.PAID, SaleStatus.DELIVERED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede cancelar una venta en estado {current_status.value}"
            )
        
        logger.info(f"Venta cancelada exitosamente: ID {sale_id}")
        return  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelando venta {sale_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al cancelar venta"
        )

@router.get("/stats/overview", response_model=SaleStats, summary="Estadísticas de ventas")
async def get_sales_stats():
    """
    Obtener estadísticas generales de ventas
    
    Incluye:
    - Totales generales y por período
    - Ventas por estado
    - Método de pago más usado
    - Promedios y totales
    """
    try:
        logger.info("Obteniendo estadísticas de ventas")
        
        # TODO: Implementar consultas reales a base de datos
        stats = SaleStats(
            total_sales=1250,
            total_revenue=125000000.00,
            avg_sale_amount=100000.00,
            today_sales=8,
            today_revenue=850000.00,
            monthly_sales=180,
            monthly_revenue=18500000.00,
            top_payment_method="credit_card",
            pending_sales=25,
            completed_sales=1180
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de ventas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estadísticas"
        )

@router.get("/reports/period", response_model=SalesReport, summary="Reporte por período")
async def get_sales_report(
    start_date: date = Query(..., description="Fecha inicio del reporte"),
    end_date: date = Query(..., description="Fecha fin del reporte")
):
    """
    Generar reporte de ventas por período específico
    
    - **start_date**: Fecha de inicio (YYYY-MM-DD)
    - **end_date**: Fecha de fin (YYYY-MM-DD)
    
    Incluye:
    - Resumen general del período
    - Ventas por día
    - Top productos y clientes
    - Desglose por método de pago y estado
    """
    try:
        logger.info(f"Generando reporte de ventas: {start_date} a {end_date}")
        
        # Validar rango de fechas
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        # TODO: Implementar consultas reales a base de datos
        report = SalesReport(
            start_date=start_date,
            end_date=end_date,
            total_sales=95,
            total_revenue=9500000.00,
            total_items_sold=285,
            avg_sale_amount=100000.00,
            sales_by_status={
                "paid": 80,
                "pending": 10,
                "cancelled": 5
            },
            sales_by_payment_method={
                "credit_card": 45,
                "cash": 25,
                "bank_transfer": 15,
                "debit_card": 10
            },
            sales_by_day=[
                {"date": "2024-01-15", "sales": 12, "revenue": 1200000.00},
                {"date": "2024-01-16", "sales": 8, "revenue": 850000.00}
            ],
            top_products=[
                {"product_id": 1, "name": "Smartphone", "quantity_sold": 25, "revenue": 2250000.00},
                {"product_id": 2, "name": "Laptop", "quantity_sold": 15, "revenue": 1800000.00}
            ],
            top_clients=[
                {"client_id": 1, "name": "Juan Pérez", "total_purchases": 3, "total_amount": 450000.00},
                {"client_id": 2, "name": "Empresa ABC", "total_purchases": 2, "total_amount": 650000.00}
            ]
        )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando reporte de ventas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al generar reporte"
        )

@router.post("/{sale_id}/refund", summary="Procesar reembolso")
async def process_refund(sale_id: int, refund_request: RefundRequest):
    """
    Procesar solicitud de reembolso
    
    - **sale_id**: ID de la venta a reembolsar
    - **reason**: Razón del reembolso (requerida)
    - **amount**: Monto a reembolsar (opcional, default = total)
    - **refund_shipping**: Incluir costo de envío en reembolso
    
    **Restricciones**:
    - Solo ventas pagadas pueden ser reembolsadas
    - El monto no puede exceder el total de la venta
    """
    try:
        logger.info(f"Procesando reembolso para venta ID: {sale_id}")
        
        # TODO: Verificar que la venta existe y está pagada
        # TODO: Validar monto del reembolso
        # TODO: Registrar transacción de reembolso
        # TODO: Actualizar estado de la venta
        # TODO: Restaurar stock si es necesario
        
        if sale_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {sale_id} no encontrada"
            )
        
        # Verificar estado de la venta
        current_status = SaleStatus.PAID  # Obtener del BD
        if current_status != SaleStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se pueden reembolsar ventas pagadas. Estado actual: {current_status.value}"
            )
        
        # Validar monto del reembolso
        total_sale_amount = 1631500.00  # Obtener del BD
        refund_amount = refund_request.amount or total_sale_amount
        
        if refund_amount > total_sale_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El monto del reembolso ({refund_amount}) no puede exceder el total de la venta ({total_sale_amount})"
            )
        
        return {
            "message": "Reembolso procesado exitosamente",
            "sale_id": sale_id,
            "refund_amount": refund_amount,
            "refund_reason": refund_request.reason,
            "refund_date": datetime.now().isoformat(),
            "new_status": SaleStatus.REFUNDED.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando reembolso para venta {sale_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar reembolso"
        )

@router.get("/client/{client_id}", response_model=SaleList, summary="Ventas por cliente")
async def get_client_sales(
    client_id: int,
    pagination: dict = Depends(get_pagination_params)
):
    """
    Obtener todas las ventas de un cliente específico
    
    - **client_id**: ID único del cliente
    - Incluye paginación estándar
    """
    try:
        logger.info(f"Obteniendo ventas del cliente ID: {client_id}")
        
        # Usar filtros existentes con client_id específico
        filters = {"client_id": client_id}
        return await list_sales(pagination=pagination, filters=filters)
        
    except Exception as e:
        logger.error(f"Error obteniendo ventas del cliente {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener ventas del cliente"
        )
