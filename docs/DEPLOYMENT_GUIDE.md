# 🚚 Guía de Despliegue - Store Management API

Esta guía proporciona instrucciones detalladas para desplegar la aplicación en diferentes entornos.

## 📋 Índice

1. [Preparativos Previos](#preparativos-previos)
2. [Despliegue Local](#despliegue-local)
3. [Despliegue en Staging](#despliegue-en-staging)
4. [Despliegue en Producción](#despliegue-en-producción)
5. [Despliegue en AWS EC2](#despliegue-en-aws-ec2)
6. [Configuración de Nexus](#configuración-de-nexus)
7. [Monitoreo Post-Despliegue](#monitoreo-post-despliegue)
8. [Rollback](#rollback)

## 🔧 Preparativos Previos

### 1. Verificar Prerrequisitos

```bash
# Verificar versiones
docker --version          # >= 20.10
docker-compose --version  # >= 2.0
git --version             # >= 2.30

# Verificar acceso a Docker
docker ps

# Verificar espacio en disco (mínimo 10GB)
df -h
```

### 2. Configurar Variables de Entorno

Crear archivo `.env` en el directorio del proyecto:

```bash
# .env
ENVIRONMENT=production
REGISTRY_URL=your-nexus-url:8085
IMAGE_TAG=v1.0.0
NEXUS_USERNAME=cicd-user
NEXUS_PASSWORD=your-secure-password
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-secure-password
GRAFANA_DOMAIN=your-domain.com
```

### 3. Descargar Imágenes Base

```bash
# Pre-descargar imágenes para acelerar el despliegue
docker pull python:3.11-slim
docker pull prom/prometheus:v2.47.0
docker pull grafana/grafana:10.2.0
docker pull sonatype/nexus3:3.42.0
```

## 🏠 Despliegue Local

### Para Desarrollo

```bash
# 1. Clonar repositorio
git clone https://github.com/your-org/artefacts_devops.git
cd artefacts_devops

# 2. Configurar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 3. Ejecutar aplicación
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Con Docker Compose

```bash
# 1. Construir y ejecutar servicios
docker-compose up -d

# 2. Verificar estado
docker-compose ps

# 3. Ver logs
docker-compose logs -f

# 4. Configurar Nexus (primera vez)
./scripts/setup-nexus.sh

# 5. Verificar aplicación
curl http://localhost:8000/api/v1/health
```

### URLs de Servicios Locales

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Nexus**: http://localhost:8081 (admin/admin123)

## 🧪 Despliegue en Staging

### 1. Preparar Servidor

```bash
# Conectarse al servidor staging
ssh user@staging-server

# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Configurar Aplicación

```bash
# Crear directorio de aplicación
sudo mkdir -p /opt/store-api
sudo chown $USER:$USER /opt/store-api
cd /opt/store-api

# Clonar código
git clone https://github.com/your-org/artefacts_devops.git .

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con valores de staging
```

### 3. Ejecutar Despliegue

```bash
# Ejecutar script de despliegue
./scripts/deploy.sh staging latest

# O manualmente
docker-compose -f docker-compose.prod.yml up -d

# Verificar servicios
docker-compose -f docker-compose.prod.yml ps
```

## 🚀 Despliegue en Producción

### 1. Configuración de Seguridad

```bash
# Configurar firewall
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 8000  # API (opcional, usar proxy)
sudo ufw allow 3000  # Grafana (opcional, usar proxy)
sudo ufw allow 9090  # Prometheus (opcional, usar proxy)
```

### 2. Configurar Nginx (Recomendado)

```nginx
# /etc/nginx/sites-available/store-api
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /grafana/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Configurar SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d your-domain.com

# Verificar renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. Despliegue con Blue-Green

```bash
# Configurar variables de producción
export ENVIRONMENT=production
export REGISTRY_URL=your-nexus-url:8085
export IMAGE_TAG=v1.0.0

# Ejecutar despliegue automatizado
./scripts/deploy.sh production v1.0.0

# El script realizará:
# - Backup del estado actual
# - Download de nueva imagen
# - Health checks
# - Rollback automático si falla
```

## ☁️ Despliegue en AWS EC2

### 1. Crear Instancia EC2

```bash
# Especificaciones recomendadas:
# - Tipo: t3.medium (2 vCPU, 4GB RAM)
# - Storage: 20GB gp3
# - OS: Ubuntu 22.04 LTS
# - Security Group: Puertos 22, 80, 443, 8000, 3000, 9090
```

### 2. Configurar Instancia

```bash
# Conectar a instancia
ssh -i your-key.pem ubuntu@your-ec2-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sesión para aplicar permisos
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Configurar Almacenamiento Persistente

```bash
# Crear volúmenes para datos persistentes
sudo mkdir -p /opt/data/{prometheus,grafana,nexus}
sudo chown -R ubuntu:ubuntu /opt/data

# Configurar backup automático
sudo crontab -e
# Agregar: 0 2 * * * /opt/store-api/scripts/backup.sh
```

### 4. Configurar Elastic Load Balancer (Opcional)

```yaml
# ALB Configuration
Type: Application Load Balancer
Scheme: Internet-facing
Listeners:
  - Port: 80 (HTTP) -> Target Group (Port 8000)
  - Port: 443 (HTTPS) -> Target Group (Port 8000)
Health Check:
  - Path: /api/v1/health
  - Interval: 30s
  - Timeout: 10s
```

## 🏪 Configuración de Nexus

### 1. Configuración Inicial

```bash
# Ejecutar configuración automática
./scripts/setup-nexus.sh

# O configurar manualmente:
# 1. Acceder a http://localhost:8081
# 2. Obtener contraseña inicial: docker exec nexus-repository cat /nexus-data/admin.password
# 3. Seguir wizard de configuración
# 4. Crear repositorios Docker
```

### 2. Configurar CI/CD

```bash
# Agregar secrets en GitHub:
# NEXUS_USERNAME=cicd-user
# NEXUS_PASSWORD=your-password

# Configurar Docker registry
docker login your-nexus-url:8085 -u cicd-user -p your-password
```

### 3. Configurar Registry en Producción

```bash
# Configurar Docker daemon para registry inseguro (si no usa HTTPS)
sudo nano /etc/docker/daemon.json
{
  "insecure-registries": ["your-nexus-url:8085"]
}

sudo systemctl restart docker
```

## 📊 Monitoreo Post-Despliegue

### 1. Verificar Servicios

```bash
# Script de verificación
./scripts/health-check.sh

# Verificación manual
curl -f http://localhost:8000/api/v1/health
curl -f http://localhost:9090/-/healthy
curl -f http://localhost:3000/api/health
```

### 2. Configurar Alertas

```bash
# Configurar alertas en Grafana
# 1. Acceder a Grafana
# 2. Configurar notification channels (Slack, email)
# 3. Crear alertas para métricas críticas
```

### 3. Monitoreo de Logs

```bash
# Configurar log rotation
sudo nano /etc/logrotate.d/docker-containers

/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    missingok
    notifempty
    copytruncate
    compress
}

# Configurar centralización de logs (opcional)
# - ELK Stack
# - AWS CloudWatch
# - Grafana Loki
```

## 🔄 Rollback

### 1. Rollback Automático

El script de despliegue incluye rollback automático en caso de falla:

```bash
# El rollback se activa automáticamente si:
# - Health checks fallan
# - Servicios no responden
# - Timeout en verificaciones
```

### 2. Rollback Manual

```bash
# Identificar versión anterior
docker images | grep store-management-api

# Rollback a versión específica
./scripts/deploy.sh production v1.0.0-previous

# O rollback manual
export IMAGE_TAG=v1.0.0-previous
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Rollback de Base de Datos (si aplica)

```bash
# Restaurar backup de datos
sudo tar -xzf /opt/backups/backup_20231201_120000/prometheus_data.tar.gz -C /opt/data/prometheus/
sudo tar -xzf /opt/backups/backup_20231201_120000/grafana_data.tar.gz -C /opt/data/grafana/

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart
```

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. Contenedor no inicia

```bash
# Verificar logs
docker-compose logs container-name

# Verificar recursos
docker stats

# Verificar configuración
docker-compose config
```

#### 2. Nexus no accesible

```bash
# Verificar si el contenedor está corriendo
docker ps | grep nexus

# Verificar logs
docker logs nexus-repository

# Verificar espacio en disco
df -h
```

#### 3. Métricas no se recolectan

```bash
# Verificar configuración de Prometheus
curl http://localhost:9090/api/v1/targets

# Verificar conectividad de red
docker network ls
docker network inspect monitoring
```

### Scripts de Utilidad

```bash
# Backup completo
./scripts/backup.sh

# Limpieza de imágenes viejas
docker image prune -a

# Verificación de salud completa
./scripts/health-check.sh

# Logs de todos los servicios
docker-compose logs --tail=100
```