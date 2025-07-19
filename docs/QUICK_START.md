# ⚡ Guía de Inicio Rápido - Store Management API

Esta guía te permitirá tener la aplicación funcionando en menos de 10 minutos.

## 🚀 Setup en 5 pasos

### 1. Clonar y Preparar

```bash
# Clonar repositorio
git clone https://github.com/your-org/artefacts_devops.git
cd artefacts_devops

# Verificar prerrequisitos
docker --version && docker-compose --version
```

### 2. Iniciar Servicios

```bash
# Iniciar todos los servicios en background
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f fastapi-app
```

### 3. Configurar Nexus (Opcional)

```bash
# Esperar que Nexus esté listo (2-3 minutos)
docker logs -f nexus-repository

# Configurar repositorios automáticamente
./scripts/setup-nexus.sh
```

### 4. Verificar Servicios

```bash
# API Health Check
curl http://localhost:8000/api/v1/health

# Prometheus Targets
curl http://localhost:9090/api/v1/targets
```

### 5. Acceder a las Interfaces

- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Nexus**: http://localhost:8081

## 🧪 Probar la API

### Crear Cliente

```bash
curl -X POST "http://localhost:8000/api/v1/clients" \
     -H "Content-Type: application/json" \
     -d '{"name": "Juan Pérez"}'
```

### Crear Producto

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
     -H "Content-Type: application/json" \
     -d '{"name": "Laptop", "price": 999.99}'
```

### Registrar Venta

```bash
# Primero obtener IDs de cliente y producto
curl http://localhost:8000/api/v1/clients
curl http://localhost:8000/api/v1/products

# Usar los IDs obtenidos
curl -X POST "http://localhost:8000/api/v1/sales" \
     -H "Content-Type: application/json" \
     -d '{"client_id": "CLIENT_ID_HERE", "product_id": "PRODUCT_ID_HERE", "quantity": 2}'
```

## 🔍 Comandos Útiles

### Docker

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs específicos
docker-compose logs prometheus
docker-compose logs grafana

# Reiniciar un servicio
docker-compose restart fastapi-app

# Parar todos los servicios
docker-compose down

# Limpiar volúmenes (CUIDADO: borra datos)
docker-compose down -v
```

### Monitoreo

```bash
# Métricas de la aplicación
curl http://localhost:8000/metrics

# Health check detallado
curl http://localhost:8000/api/v1/health | jq

# Verificar targets de Prometheus
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'
```

### Testing

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Test específico
pytest tests/test_main.py::test_health_check -v
```

## 🐛 Troubleshooting Rápido

### Puerto ya en uso

```bash
# Verificar qué usa el puerto
lsof -i :8000

# Matar proceso si es necesario
kill -9 PID
```

### Nexus no responde

```bash
# Verificar logs
docker logs nexus-repository

# Reiniciar Nexus
docker-compose restart nexus

# Verificar espacio en disco
df -h
```

### Métricas no aparecen

```bash
# Verificar conectividad
docker exec -it prometheus wget -q --spider http://fastapi-app:8000/metrics && echo "OK" || echo "FAIL"

# Recargar configuración
curl -X POST http://localhost:9090/-/reload
```

### Problemas de memoria

```bash
# Ver uso de recursos
docker stats

# Limpiar imágenes no usadas
docker image prune -a

# Limpiar contenedores parados
docker container prune
```

## 🔄 Desarrollo

### Setup Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Hot Reload con Docker

```bash
# Modificar docker-compose.yaml para development:
# volumes:
#   - ./app:/app/app:ro  # Mount para hot reload

docker-compose up -d fastapi-app
```

## 📊 Dashboard Rápido en Grafana

1. Ir a http://localhost:3000
2. Login: admin/admin123
3. Dashboard pre-configurado ya está disponible
4. O crear nuevo:
   - Add Panel
   - Query: `rate(http_requests_total[5m])`
   - Visualization: Time series

## 🚀 Deploy Rápido

### Local con imágenes de producción

```bash
# Build imagen de producción
docker build -t store-management-api .

# Usar docker-compose de producción
docker-compose -f docker-compose.prod.yml up -d
```

### Deploy automatizado

```bash
# Deploy a staging
./scripts/deploy.sh staging latest

# Deploy a producción
./scripts/deploy.sh production v1.0.0
```

## 📝 Variables de Entorno Importantes

```bash
# Crear archivo .env
cat > .env << EOF
ENVIRONMENT=development
REGISTRY_URL=localhost:8085
IMAGE_TAG=latest
NEXUS_USERNAME=cicd-user
NEXUS_PASSWORD=cicd-password-123
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin123
EOF
```

## 🎯 Checklist de Verificación

- [ ] Todos los contenedores están corriendo (`docker-compose ps`)
- [ ] API responde (`curl http://localhost:8000/api/v1/health`)
- [ ] Métricas se recolectan (`curl http://localhost:8000/metrics`)
- [ ] Grafana muestra datos (http://localhost:3000)
- [ ] Prometheus muestra targets activos (http://localhost:9090)
- [ ] Tests pasan (`pytest`)

## 🆘 Obtener Ayuda

- **Logs completos**: `docker-compose logs`
- **Estado del sistema**: `docker stats`
- **Documentación completa**: Ver `README.md`
- **Issues**: GitHub Issues del proyecto

---

**💡 Tip**: Si algo no funciona, `docker-compose down && docker-compose up -d` suele resolver la mayoría de problemas. 