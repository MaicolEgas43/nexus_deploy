# 🚀 Guía de Implementación CI/CD - Store Management API

## 📋 Resumen Ejecutivo

Esta guía proporciona una solución completa de CI/CD para **Store Management API**, un proyecto Python/FastAPI containerizado que implementa un flujo seguro y automatizado desde desarrollo hasta producción.

### 🎯 Objetivos Alcanzados

✅ **Pipeline Automatizado**: Desde commit hasta deployment en EC2  
✅ **Seguridad Integrada**: Escaneo de vulnerabilidades con Trivy  
✅ **Quality Gates**: Tests, lint, coverage automáticos  
✅ **Versionado Semántico**: Automático con tags de Git  
✅ **Monitoreo Completo**: Prometheus + Grafana + alertas  
✅ **Registry Corporativo**: Nexus para Docker y Python packages  
✅ **Deployment Flexible**: EC2 o local con rollback rápido  

### 🏗️ Arquitectura Final

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Develop   │    │    Main     │    │    EC2      │
│   Branch    │───▶│   Branch    │───▶│ Production  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ PR Pipeline │    │ CI/CD Full  │    │  Monitoring │
│• Build      │    │• Test       │    │• Prometheus │
│• Test       │    │• Security   │    │• Grafana    │
│• Security   │    │• Publish    │    │• Alerts     │
└─────────────┘    │• Deploy     │    └─────────────┘
                   │• Monitor    │
                   └─────────────┘
```

## 🔄 Flujo de Trabajo Completo

### 1. Desarrollo y PR
```bash
# Developer workflow
git checkout develop
git checkout -b feature/nueva-funcionalidad
# ... desarrollo ...
git push origin feature/nueva-funcionalidad
# Crear PR → Se ejecuta .github/workflows/pr-validation.yml
```

### 2. Merge a Main
```bash
# Después de review y aprobación
git checkout main
git merge develop
git push origin main
# Se ejecuta automáticamente .github/workflows/ci-cd.yml
```

### 3. Deployment Automático
```bash
# Pipeline automático:
# 1. Calcula nueva versión (v1.2.3)
# 2. Ejecuta tests completos
# 3. Build imagen Docker multi-stage
# 4. Scan de seguridad con Trivy
# 5. Publica a Nexus (PyPI + Docker)
# 6. Deploy a EC2 vía SSH
# 7. Health checks
# 8. Notificaciones Slack/Teams
```

## 📚 Estructura de Archivos Creados

```
proyecto/
├── .github/workflows/
│   ├── ci-cd.yml              # ✅ Pipeline principal
│   └── pr-validation.yml      # ✅ Validación de PRs
├── docker-compose.prod.yaml   # ✅ Stack de producción optimizado
├── Dockerfile                 # ✅ Multi-stage (ya existía, optimizado)
├── prometheus/
│   └── prometheus.yml         # ✅ Configuración de monitoreo
└── docs/
    ├── SECRETS_AND_VARIABLES.md         # ✅ Configuración de secrets
    └── CI_CD_IMPLEMENTATION_GUIDE.md    # ✅ Esta guía
```

## 🚦 Checklist de Implementación

### Fase 1: Configuración Base (30 min)

- [ ] **1.1 Configurar Secrets en GitHub**
  ```bash
  gh secret set NEXUS_USERNAME --body "admin"
  gh secret set NEXUS_PASSWORD --body "your-nexus-password"
  gh secret set EC2_SSH_KEY --body "$(cat ~/.ssh/ec2-key)"
  gh secret set EC2_HOST --body "54.123.45.67"
  gh secret set EC2_USER --body "ubuntu"
  ```

- [ ] **1.2 Configurar Variables en GitHub**
  ```bash
  gh variable set NEXUS_URL --body "http://ec2-13-223-57-61.compute-1.amazonaws.com"
  gh variable set NEXUS_DOCKER_REGISTRY --body "http://ec2-13-223-57-61.compute-1.amazonaws.com:8081/"
  gh variable set DEPLOY_TARGET --body "ec2"
  ```

- [ ] **1.3 Configurar Branch Protection Rules**
  - Proteger rama `main`
  - Requiere review de PR
  - Requiere status checks
  - No permitir force push

### Fase 2: Configuración de Infraestructura (45 min)

- [ ] **2.1 Configurar Nexus Repository**
  ```bash
  # Crear repositorios:
  # - Docker (hosted): docker-hosted
  # - PyPI (hosted): pypi-releases
  # - PyPI (proxy): pypi-proxy
  # - PyPI (group): pypi-public
  ```

- [ ] **2.2 Preparar EC2 Instance**
  ```bash
  # Instalar Docker y Docker Compose
  sudo apt update
  sudo apt install -y docker.io docker-compose-v2
  sudo usermod -aG docker $USER
  
  # Crear directorio de aplicación
  sudo mkdir -p /opt/store-management-api
  sudo chown $USER:$USER /opt/store-management-api
  ```

- [ ] **2.3 Configurar SSH Keys**
  ```bash
  # Generar key específica para deployment
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/deploy-key -N ""
  
  # Copiar key pública al EC2
  ssh-copy-id -i ~/.ssh/deploy-key.pub ubuntu@54.123.45.67
  
  # Añadir private key a GitHub Secrets
  gh secret set EC2_SSH_KEY --body "$(cat ~/.ssh/deploy-key)"
  ```

### Fase 3: Testing del Pipeline (30 min)

- [ ] **3.1 Test PR Pipeline**
  ```bash
  # Crear PR de prueba
  git checkout develop
  git checkout -b test/ci-cd-setup
  echo "# Test CI/CD" >> TEST.md
  git add TEST.md
  git commit -m "test: verificar pipeline de PR"
  git push origin test/ci-cd-setup
  # Crear PR y verificar que corre pr-validation.yml
  ```

- [ ] **3.2 Test Deployment Pipeline**
  ```bash
  # Merge a main para trigger deployment
  git checkout main
  git merge develop
  git push origin main
  # Verificar que corre ci-cd.yml completo
  ```

- [ ] **3.3 Verificar Deployment**
  ```bash
  # Verificar aplicación en EC2
  curl -f http://54.123.45.67:8000/health
  curl -f http://54.123.45.67:8000/metrics
  
  # Verificar Grafana
  open http://54.123.45.67:3000
  # admin / admin (cambiar password)
  ```

### Fase 4: Configuración de Monitoreo (20 min)

- [ ] **4.1 Configurar Prometheus Targets**
  ```yaml
  # Editar prometheus/prometheus.yml
  # Reemplazar ${EC2_HOST} con IP real
  - targets: ['54.123.45.67:8000']  # IP real de EC2
  ```

- [ ] **4.2 Configurar Alertas (opcional)**
  ```bash
  # Crear rules/alerts.yml
  mkdir -p prometheus/rules
  # Añadir reglas de alertas básicas
  ```

- [ ] **4.3 Configurar Notificaciones**
  ```bash
  # Slack
  gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/..."
  
  # Teams (alternativo)
  gh secret set TEAMS_WEBHOOK_URL --body "https://outlook.office.com/..."
  ```

## ⚡ Quick Start - Implementación Rápida

Para implementar rápidamente en un nuevo proyecto:

```bash
#!/bin/bash
# scripts/quick-setup.sh

echo "🚀 Configuración rápida de CI/CD..."

# 1. Clonar y configurar repositorio
git clone https://github.com/tu-org/store-management-api.git
cd store-management-api

# 2. Configurar secrets básicos
read -p "Nexus URL: " NEXUS_URL
read -p "Nexus Username: " NEXUS_USER
read -s -p "Nexus Password: " NEXUS_PASS
echo
read -p "EC2 Host IP: " EC2_HOST

gh secret set NEXUS_USERNAME --body "$NEXUS_USER"
gh secret set NEXUS_PASSWORD --body "$NEXUS_PASS"
gh secret set EC2_HOST --body "$EC2_HOST"
gh secret set EC2_USER --body "ubuntu"

# 3. Configurar variables
gh variable set NEXUS_URL --body "$NEXUS_URL"
gh variable set NEXUS_DOCKER_REGISTRY --body "$NEXUS_URL:8085"
gh variable set DEPLOY_TARGET --body "ec2"

# 4. Configurar SSH key
if [ ! -f ~/.ssh/deploy-key ]; then
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/deploy-key -N ""
fi

gh secret set EC2_SSH_KEY --body "$(cat ~/.ssh/deploy-key)"

echo "✅ Configuración básica completada"
echo "📋 Siguiente: copiar key pública al EC2:"
echo "ssh-copy-id -i ~/.ssh/deploy-key.pub ubuntu@$EC2_HOST"
```

## 🔧 Personalización por Proyecto

### Variables a Modificar

```yaml
# En .github/workflows/ci-cd.yml
env:
  APP_NAME: "tu-app-name"                    # Cambiar nombre
  PYTHON_VERSION: "3.11"                    # Versión de Python
  
# En docker-compose.prod.yaml
services:
  tu-app:                                    # Cambiar nombre del servicio
    image: ${IMAGE_TAG:-nexus.company.com:8085/tu-app:latest}
    container_name: tu-app-prod              # Cambiar nombre del container
```

### Estructura de Monitoreo

```yaml
# En prometheus/prometheus.yml
- job_name: 'tu-app-name'                    # Cambiar job name
  static_configs:
    - targets: ['tu-app:8000']               # Cambiar target
      labels:
        app: 'tu-app'                        # Cambiar labels
        team: 'tu-team'
```

## 🐛 Troubleshooting

### Problemas Comunes

**1. Pipeline Falla en Tests**
```bash
# Verificar dependencias localmente
pip install -r requirements.txt
pytest tests/ -v

# Verificar formato
black --check app/ tests/
flake8 app/ tests/
```

**2. Build de Docker Falla**
```bash
# Test local del Dockerfile
docker build -t test-image .
docker run --rm test-image python -c "import app.main"
```

**3. Deployment a EC2 Falla**
```bash
# Verificar conectividad SSH
ssh -i ~/.ssh/deploy-key ubuntu@54.123.45.67 "echo 'SSH OK'"

# Verificar Docker en EC2
ssh -i ~/.ssh/deploy-key ubuntu@54.123.45.67 "docker --version"

# Verificar login a Nexus desde EC2
ssh -i ~/.ssh/deploy-key ubuntu@54.123.45.67 \
  "docker login nexus.company.com:8085 -u admin -p password"
```

**4. Métricas no Aparecen en Prometheus**
```bash
# Verificar endpoint de métricas
curl http://54.123.45.67:8000/metrics

# Verificar configuración de Prometheus
docker exec prometheus-prod cat /etc/prometheus/prometheus.yml

# Verificar targets en Prometheus UI
open http://54.123.45.67:9090/targets
```

**5. Secretos No Se Detectan**
```bash
# Verificar secretos configurados
gh secret list

# Verificar variables configuradas
gh variable list

# Test de secrets en workflow
echo "Testing secret access in workflow"
```

### Logs y Debugging

```bash
# Ver logs del pipeline
gh run list
gh run view [RUN_ID] --log

# Ver logs de la aplicación en EC2
ssh -i ~/.ssh/deploy-key ubuntu@54.123.45.67 \
  "cd /opt/store-management-api && docker-compose logs -f store-api"

# Ver logs de Prometheus
docker logs prometheus-prod

# Ver logs de Grafana
docker logs grafana-prod
```

## 📊 Métricas y KPIs de CI/CD

### Métricas de Pipeline

- **Lead Time**: Tiempo desde commit hasta producción (Target: < 20 min)
- **Deployment Frequency**: Frecuencia de deployments (Target: > 1/día)
- **Change Failure Rate**: % de deployments que fallan (Target: < 5%)
- **Recovery Time**: Tiempo para recuperar de fallas (Target: < 10 min)

### Monitoreo de Aplicación

```bash
# Health checks automáticos
curl http://54.123.45.67:8000/health
curl http://54.123.45.67:8000/metrics

# Verificar métricas en Prometheus
curl http://54.123.45.67:9090/api/v1/query?query=up

# Dashboard de Grafana
open http://54.123.45.67:3000/d/store-management
```

## 🎯 Próximos Pasos

### Mejoras Recomendadas

1. **Stage Environment**
   - Añadir ambiente de staging
   - Deploy automático en develop

2. **Advanced Security**
   - SAST con SonarQube
   - Container scanning avanzado
   - Secrets scanning

3. **Observability**
   - Distributed tracing con Jaeger
   - Logs centralizados con ELK
   - APM con New Relic/DataDog

4. **Infrastructure as Code**
   - Terraform para EC2
   - Ansible para configuración
   - GitOps con ArgoCD

5. **Advanced Deployment**
   - Blue-Green deployments
   - Canary releases
   - Feature flags

### Roadmap Sugerido

| Semana | Tarea | Prioridad |
|--------|-------|-----------|
| 1 | Implementación básica CI/CD | Alta |
| 2 | Configuración completa de monitoreo | Alta |
| 3 | Ambiente de staging | Media |
| 4 | Mejoras de seguridad | Media |
| 5-6 | Infrastructure as Code | Baja |
| 7-8 | Advanced deployment strategies | Baja |

## 📞 Soporte y Contacto

Para dudas o problemas:

1. **Documentación**: Revisar este archivo y `SECRETS_AND_VARIABLES.md`
2. **Logs**: Verificar logs de GitHub Actions y aplicación
3. **Monitoreo**: Revisar métricas en Prometheus/Grafana
4. **Team**: Contactar al equipo DevOps

---

**✨ ¡Felicidades! Tu pipeline CI/CD está listo para producción.** 