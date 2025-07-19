"""
Router para gestión de clientes
Incluye endpoints CRUD completos, estadísticas, búsqueda y validaciones
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from datetime import datetime
import logging

# Importar modelos desde el paquete local
from ..models.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientList,
    ClientStats,
    ClientType,
    ClientStatus
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router con prefix y tags para documentación
router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={
        404: {"description": "Cliente no encontrado"},
        422: {"description": "Error de validación"},
        500: {"description": "Error interno del servidor"}
    }
)

# Dependencia simulada para paginación
def get_pagination_params(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página")
):
    """Parámetros de paginación estándar"""
    return {"page": page, "per_page": per_page}

# Dependencia simulada para filtros de búsqueda
def get_client_filters(
    name: Optional[str] = Query(None, description="Filtrar por nombre"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    client_type: Optional[ClientType] = Query(None, description="Filtrar por tipo"),
    status: Optional[ClientStatus] = Query(None, description="Filtrar por estado"),
    city: Optional[str] = Query(None, description="Filtrar por ciudad"),
    country: Optional[str] = Query(None, description="Filtrar por país")
):
    """Filtros de búsqueda para clientes"""
    return {
        "name": name,
        "email": email,
        "client_type": client_type,
        "status": status,
        "city": city,
        "country": country
    }

@router.get("/", response_model=ClientList, summary="Listar clientes")
async def list_clients(
    pagination: dict = Depends(get_pagination_params),
    filters: dict = Depends(get_client_filters)
):
    """
    Listar clientes con paginación y filtros opcionales
    
    - **page**: Número de página (mínimo 1)
    - **per_page**: Elementos por página (1-100)
    - **name**: Filtrar por nombre (búsqueda parcial)
    - **email**: Filtrar por email exacto
    - **client_type**: Filtrar por tipo de cliente
    - **status**: Filtrar por estado
    - **city**: Filtrar por ciudad
    - **country**: Filtrar por país
    """
    try:
        logger.info(f"Listando clientes - Página {pagination['page']}, Filtros: {filters}")
        
        # TODO: Implementar consulta real a base de datos
        # Simulación de datos para desarrollo
        mock_clients = [
            ClientResponse(
                id=1,
                name="Juan Pérez",
                email="juan.perez@example.com",
                phone="+57 300 123 4567",
                address="Calle 123 #45-67",
                city="Bogotá",
                country="Colombia",
                client_type=ClientType.INDIVIDUAL,
                status=ClientStatus.ACTIVE,
                notes="Cliente preferencial",
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 20, 15, 45),
                total_purchases=1500000.00,
                purchase_count=5
            ),
            ClientResponse(
                id=2,
                name="Empresa ABC S.A.S.",
                email="contacto@empresaabc.com",
                phone="+57 310 987 6543",
                address="Carrera 15 #78-90",
                city="Medellín", 
                country="Colombia",
                client_type=ClientType.BUSINESS,
                status=ClientStatus.ACTIVE,
                notes="Cliente corporativo",
                created_at=datetime(2024, 1, 10, 8, 15),
                updated_at=datetime(2024, 1, 25, 12, 30),
                total_purchases=5000000.00,
                purchase_count=12
            )
        ]
        
        # Aplicar filtros básicos (simulación)
        filtered_clients = mock_clients
        if filters.get("name"):
            filtered_clients = [c for c in filtered_clients if filters["name"].lower() in c.name.lower()]
        if filters.get("client_type"):
            filtered_clients = [c for c in filtered_clients if c.client_type == filters["client_type"]]
        if filters.get("status"):
            filtered_clients = [c for c in filtered_clients if c.status == filters["status"]]
            
        # Paginación simulada
        total = len(filtered_clients)
        start_idx = (pagination["page"] - 1) * pagination["per_page"]
        end_idx = start_idx + pagination["per_page"]
        paginated_clients = filtered_clients[start_idx:end_idx]
        
        return ClientList(
            clients=paginated_clients,
            total=total,
            page=pagination["page"],
            per_page=pagination["per_page"],
            has_next=end_idx < total,
            has_prev=pagination["page"] > 1
        )
        
    except Exception as e:
        logger.error(f"Error listando clientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar clientes"
        )

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, summary="Crear cliente")
async def create_client(client: ClientCreate):
    """
    Crear un nuevo cliente
    
    - **name**: Nombre completo (requerido, 2-100 caracteres)
    - **email**: Email válido único (requerido)
    - **phone**: Teléfono opcional con validación
    - **address**: Dirección opcional
    - **city**: Ciudad opcional
    - **country**: País opcional
    - **client_type**: Tipo de cliente (individual/business/premium)
    - **notes**: Notas adicionales opcionales
    """
    try:
        logger.info(f"Creando cliente: {client.email}")
        
        # TODO: Validar email único en base de datos
        # TODO: Implementar creación real en base de datos
        
        # Simulación de creación
        new_client = ClientResponse(
            id=999,  # ID generado por la base de datos
            **client.dict(),
            status=ClientStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=None,
            total_purchases=0.0,
            purchase_count=0
        )
        
        logger.info(f"Cliente creado exitosamente: ID {new_client.id}")
        return new_client
        
    except ValueError as e:
        logger.warning(f"Error de validación creando cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creando cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear cliente"
        )

@router.get("/{client_id}", response_model=ClientResponse, summary="Obtener cliente")
async def get_client(client_id: int):
    """
    Obtener un cliente específico por ID
    
    - **client_id**: ID único del cliente
    """
    try:
        logger.info(f"Obteniendo cliente ID: {client_id}")
        
        # TODO: Implementar consulta real a base de datos
        if client_id == 1:
            return ClientResponse(
                id=1,
                name="Juan Pérez",
                email="juan.perez@example.com",
                phone="+57 300 123 4567",
                address="Calle 123 #45-67",
                city="Bogotá",
                country="Colombia",
                client_type=ClientType.INDIVIDUAL,
                status=ClientStatus.ACTIVE,
                notes="Cliente preferencial",
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 20, 15, 45),
                total_purchases=1500000.00,
                purchase_count=5
            )
        
        logger.warning(f"Cliente no encontrado: ID {client_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {client_id} no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo cliente {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener cliente"
        )

@router.put("/{client_id}", response_model=ClientResponse, summary="Actualizar cliente")
async def update_client(client_id: int, client_update: ClientUpdate):
    """
    Actualizar un cliente existente
    
    - **client_id**: ID único del cliente
    - Solo se actualizan los campos proporcionados (PATCH-like behavior)
    """
    try:
        logger.info(f"Actualizando cliente ID: {client_id}")
        
        # TODO: Verificar que el cliente existe
        # TODO: Implementar actualización real en base de datos
        
        # Simulación de actualización
        if client_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {client_id} no encontrado"
            )
        
        # Simular cliente actualizado
        updated_client = ClientResponse(
            id=client_id,
            name=client_update.name or "Juan Pérez",
            email=client_update.email or "juan.perez@example.com",
            phone=client_update.phone or "+57 300 123 4567",
            address=client_update.address or "Calle 123 #45-67",
            city=client_update.city or "Bogotá",
            country=client_update.country or "Colombia",
            client_type=client_update.client_type or ClientType.INDIVIDUAL,
            status=client_update.status or ClientStatus.ACTIVE,
            notes=client_update.notes or "Cliente preferencial",
            created_at=datetime(2024, 1, 15, 10, 30),
            updated_at=datetime.now(),
            total_purchases=1500000.00,
            purchase_count=5
        )
        
        logger.info(f"Cliente actualizado exitosamente: ID {client_id}")
        return updated_client
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando cliente {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al actualizar cliente"
        )

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar cliente")
async def delete_client(client_id: int):
    """
    Eliminar un cliente
    
    - **client_id**: ID único del cliente
    - **Nota**: Eliminación lógica (cambiar status a inactive)
    """
    try:
        logger.info(f"Eliminando cliente ID: {client_id}")
        
        # TODO: Verificar que el cliente existe
        # TODO: Verificar que no tenga ventas asociadas
        # TODO: Implementar eliminación lógica en base de datos
        
        if client_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {client_id} no encontrado"
            )
        
        logger.info(f"Cliente eliminado exitosamente: ID {client_id}")
        return  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando cliente {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al eliminar cliente"
        )

@router.get("/stats/overview", response_model=ClientStats, summary="Estadísticas de clientes")
async def get_client_stats():
    """
    Obtener estadísticas generales de clientes
    
    Incluye:
    - Total de clientes por estado
    - Clientes premium
    - Ingresos totales
    - Promedio de compra por cliente
    """
    try:
        logger.info("Obteniendo estadísticas de clientes")
        
        # TODO: Implementar consultas reales a base de datos
        stats = ClientStats(
            total_clients=150,
            active_clients=142,
            inactive_clients=8,
            premium_clients=25,
            total_revenue=45000000.00,
            avg_purchase_per_client=300000.00
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de clientes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener estadísticas"
        )

@router.get("/{client_id}/purchases", summary="Historial de compras")
async def get_client_purchases(
    client_id: int,
    pagination: dict = Depends(get_pagination_params)
):
    """
    Obtener historial de compras de un cliente específico
    
    - **client_id**: ID único del cliente
    - Incluye paginación estándar
    """
    try:
        logger.info(f"Obteniendo compras del cliente ID: {client_id}")
        
        # TODO: Verificar que el cliente existe
        # TODO: Implementar consulta real de ventas
        
        if client_id != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con ID {client_id} no encontrado"
            )
        
        # Simulación de historial de compras
        return {
            "client_id": client_id,
            "purchases": [],  # Lista de ventas
            "total_purchases": 5,
            "total_amount": 1500000.00,
            "page": pagination["page"],
            "per_page": pagination["per_page"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo compras del cliente {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener compras"
        )
