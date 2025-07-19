# 🧪 Guía de Pruebas Locales

Esta guía te ayudará a probar completamente la aplicación **Store Management API** antes del deploy a AWS.

## 📋 Pre-requisitos

- Python 3.8+
- Git
- Terminal/bash

## 🚀 Configuración Inicial

### 1. Activar el entorno virtual
```bash
source venv/bin/activate
```

### 2. Verificar instalación
```bash
pip list | grep -E "(fastapi|uvicorn|prometheus)"
```

## 🔧 Métodos de Prueba

### **Método A: Script Automatizado (Recomendado)**

```bash
./run_tests.sh
```

Este script:
- ✅ Verifica dependencias
- ✅ Inicia el servidor
- ✅ Ejecuta todas las pruebas
- ✅ Muestra URLs importantes
- ✅ Mantiene el servidor corriendo para pruebas manuales

### **Método B: Paso a Paso Manual**

#### 1. Iniciar el servidor
```bash
python main.py
```

#### 2. En otra terminal, ejecutar pruebas
```bash
python test_local.py
```

#### 3. Pruebas manuales con curl
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Crear cliente
curl -X POST http://localhost:8000/api/v1/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan Pérez"}'

# Ver clientes  
curl http://localhost:8000/api/v1/clients

# Métricas de Prometheus
curl http://localhost:8000/metrics
```

## 🌐 URLs de Prueba

| Servicio | URL | Propósito |
|----------|-----|-----------|
| **API Docs** | http://localhost:8000/docs | Documentación interactiva |
| **Health Check** | http://localhost:8000/api/v1/health | Verificar estado |
| **Root** | http://localhost:8000/api/v1/ | Info general |
| **Métricas** | http://localhost:8000/metrics | Prometheus metrics |

## 🧪 Escenarios de Prueba

### ✅ Casos de Éxito
1. **Health Check**: Debe retornar `status: "healthy"`
2. **Crear Cliente**: Debe generar ID único
3. **Crear Producto**: Debe validar precio > 0
4. **Crear Venta**: Debe validar IDs existentes
5. **Métricas**: Debe mostrar métricas de Prometheus

### ❌ Casos de Error
1. **Venta inválida**: Cliente o producto inexistente
2. **Datos malformados**: JSON inválido
3. **Campos faltantes**: Validación de Pydantic

## 🐳 Pruebas con Docker

### 1. Construir la imagen
```bash
docker build -t store-api .
```

### 2. Ejecutar contenedor
```bash
docker run -p 8000:8000 store-api
```

### 3. Probar health check
```bash
curl http://localhost:8000/api/v1/health
```

## 🐳 Pruebas con Docker Compose

### Desarrollo
```bash
docker-compose up --build
```

### Producción
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 📊 Verificar Métricas

Las métricas de Prometheus están en `/metrics`:

```bash
curl http://localhost:8000/metrics | grep -E "(http_requests|process_cpu)"
```

Deberías ver métricas como:
- `http_requests_total`
- `process_cpu_seconds_total`
- `python_gc_objects_collected_total`

## 🔍 Logs de Depuración

Si hay problemas, revisa los logs:

```bash
# Ejecutar con logs detallados
uvicorn app:app --host 0.0.0.0 --port 8000 --log-level debug
```

## ✅ Checklist Pre-Deploy

Antes de hacer deploy, verifica:

- [ ] Health check responde correctamente
- [ ] Todos los endpoints CRUD funcionan
- [ ] Métricas de Prometheus están disponibles  
- [ ] Docker build exitoso
- [ ] Docker run funciona correctamente
- [ ] Tests automatizados pasan
- [ ] No hay errores en logs
- [ ] Documentación accesible en `/docs`

## 🚨 Problemas Comunes

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Encontrar proceso usando puerto 8000
lsof -i :8000
# Matar proceso
kill -9 <PID>
```

### Error: "Permission denied"
```bash
chmod +x run_tests.sh
```

## 🎯 Siguientes Pasos

Una vez que todas las pruebas locales pasen:

1. ✅ Commit cambios a Git
2. ✅ Push a GitHub  
3. ✅ Verificar CI/CD pipeline
4. ✅ Deploy a AWS

¡Tu aplicación está lista para producción! 🚀 