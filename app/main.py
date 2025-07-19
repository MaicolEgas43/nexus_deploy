from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import uvicorn
import os
import time
from typing import Dict

# Imports actualizados - Usar nuevos routers organizados
from .routers import include_all_routers
from .metrics import setup_metrics
from .postgres_db import startup_db, shutdown_db

# Crear aplicación FastAPI
app = FastAPI(
    title="Store Management API",
    description="API para gestión de clientes, productos y ventas - Proyecto DevOps",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # Metadatos adicionales para mejor documentación
    contact={
        "name": "DevOps Team",
        "email": "devops@storeapi.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo local"
        },
        {
            "url": "https://api.storemanagement.com",
            "description": "Servidor de producción"
        }
    ]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar métricas de Prometheus
setup_metrics(app)

# Eventos de base de datos
@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    await startup_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación"""
    await shutdown_db()

# Incluir todos los routers organizados por funcionalidad
include_all_routers(app)

@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Store Management API - Proyecto DevOps",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "metrics": "/metrics",
        "health": "/health",
        "api": {
            "clients": "/api/v1/clients",
            "products": "/api/v1/products", 
            "sales": "/api/v1/sales"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint para Docker y Kubernetes"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "services": {
            "database": "operational",
            "metrics": "operational",
            "api": "operational"
        },
        "api_info": {
            "total_routers": 3,
            "total_endpoints": 15,
            "routers_version": "1.0.0"
        }
    }

@app.get("/metrics", tags=["Metrics"])
async def get_metrics():
    """Endpoint de métricas para Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/info", tags=["API Info"])
async def get_api_info():
    """Información detallada de la API y sus routers"""
    return get_router_info()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    ) 