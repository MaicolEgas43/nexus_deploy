import os
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
import asyncio

# Configuración de la base de datos PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/postgres"
)

# Instancias principales
database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL)

# Tabla de Clientes
clientes_table = Table(
    "clientes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

# Tabla de Productos
productos_table = Table(
    "productos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("price", Float, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

# Tabla de Ventas
ventas_table = Table(
    "ventas",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("client_id", Integer, nullable=False),  # Referencia a clientes.id
    Column("product_id", Integer, nullable=False), # Referencia a productos.id
    Column("quantity", Integer, nullable=False),
    Column("total_amount", Float, nullable=True),  # Calculado: price * quantity
    Column("created_at", DateTime, server_default=func.now())
)

# Funciones de conexión
async def connect_db():
    try:
        await database.connect()
        print("✅ Conexión a PostgreSQL establecida")
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        raise

async def disconnect_db():
    try:
        await database.disconnect()
        print("🔌 Desconectado de PostgreSQL")
    except Exception as e:
        print(f"❌ Error desconectando: {e}")

def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        metadata.create_all(engine)
        print("✅ Tablas creadas/verificadas en PostgreSQL")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        raise

def drop_tables():
    """Eliminar todas las tablas (solo para desarrollo/testing)"""
    try:
        metadata.drop_all(engine)
        print("🗑️ Todas las tablas eliminadas")
    except Exception as e:
        print(f"❌ Error eliminando tablas: {e}")

# Función para verificar conexión
async def check_database_connection():
    """Verificar que la conexión a la base de datos funciona"""
    try:
        await database.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Error en conexión a BD: {e}")
        return False

# Configuración de eventos de aplicación (para usar en main.py)
async def startup_db():
    """Ejecutar al iniciar la aplicación"""
    await connect_db()
    create_tables()
    
    # Verificar conexión
    if await check_database_connection():
        print("🚀 Base de datos lista para usar")
    else:
        raise Exception("No se pudo conectar a PostgreSQL")

async def shutdown_db():
    """Ejecutar al cerrar la aplicación"""
    await disconnect_db()
