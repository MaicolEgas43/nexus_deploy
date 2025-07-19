# 🚀 Guía Rápida CI/CD - Proyecto Final DevOps

## 👋 ¡Hola Estudiante de DevOps!

Esta es una guía práctica para implementar CI/CD en tu **proyecto final**. Está diseñada para que puedas entender y aplicar los conceptos básicos de DevOps de manera práctica.

## 🎯 ¿Qué Vamos a Lograr?

Al final de esta guía tendrás:

✅ **Pipeline Automático**: Cada vez que hagas `git push`, se ejecutan tests y deployment automáticamente  
✅ **Tests Automáticos**: Tu código se verifica automáticamente antes de llegar a producción  
✅ **Deployment Seguro**: Solo código que pasa tests llega a producción  
✅ **Monitoreo Básico**: Ver métricas de tu aplicación en tiempo real  
✅ **Docker Registry**: Tu propia "biblioteca" de imágenes Docker  

## 🏗️ Arquitectura Simple

```
Developer → GitHub → GitHub Actions → Nexus → EC2 → Monitoreo
    |          |           |           |      |        |
  Código    Repo      CI/CD Pipeline Registry Server  Grafana
```

**En palabras simples:**
1. Escribes código y lo subes a GitHub
2. GitHub Actions ejecuta tests automáticamente
3. Si los tests pasan, construye una imagen Docker
4. La imagen se guarda en Nexus (tu registry privado)
5. Se despliega automáticamente en tu servidor EC2
6. Puedes ver métricas en Grafana

## 📋 Checklist - Configuración Paso a Paso

### Paso 1: Configurar Secrets en GitHub (5 min) ⚙️

Los "secrets" son información sensible que GitHub guarda de forma segura:

```bash
# Ve a tu repositorio en GitHub → Settings → Secrets and variables → Actions

# Añadir estos secrets:
NEXUS_USERNAME: admin
NEXUS_PASSWORD: tu-password-de-nexus  
EC2_SSH_KEY: tu-clave-ssh-privada
EC2_HOST: la-ip-de-tu-ec2
EC2_USER: ubuntu
```

### Paso 2: Configurar Variables en GitHub (2 min) 📊

Las variables son configuración no sensible:

```bash
# En la misma sección, pestaña "Variables":
NEXUS_URL: http://tu-nexus-server.com
NEXUS_DOCKER_PORT: 8081
ENABLE_SECURITY_SCAN: true
```

### Paso 3: Preparar tu Servidor EC2 (10 min) 🖥️

Conecta a tu EC2 y ejecuta:

```bash
# Instalar Docker
sudo apt update
sudo apt install -y docker.io docker-compose-v2

# Permitir que tu usuario use Docker
sudo usermod -aG docker ec2-docker

# Crear directorio para la app
mkdir -p ~/app-fastapi
cd ~/app-fastapi

# Reiniciar sesión para aplicar permisos
exit
```

### Paso 4: Probar el Pipeline (5 min) 🧪

1. **Crear un PR de prueba:**
   ```bash
   git checkout develop
   git checkout -b test/mi-primer-ci-cd
   echo "Probando CI/CD" > TEST.md
   git add TEST.md
   git commit -m "test: probar pipeline"
   git push origin test/mi-primer-ci-cd
   ```

2. **Crear Pull Request en GitHub**
   - Ve a tu repo → Pull Requests → New
   - Verás que se ejecuta automáticamente `.github/workflows/pr-validation.yml`

3. **Hacer merge a main:**
   ```bash
   # Después de aprobar el PR
   git checkout main
   git merge develop
   git push origin main
   ```
   - Se ejecutará automáticamente `.github/workflows/ci-cd.yml`

## 🔍 ¿Qué Hace Cada Pipeline?

### Pipeline de PR (Validación) 🔍

**¿Cuándo se ejecuta?** Al crear o actualizar un Pull Request

**¿Qué hace?**
1. **Tests**: Ejecuta `pytest` para verificar que el código funciona
2. **Formato**: Verifica que el código esté bien formateado con `black`
3. **Build**: Construye la imagen Docker para verificar que no hay errores
4. **Security**: Escanea vulnerabilidades básicas (opcional)
5. **Resultado**: Comenta en el PR si está listo para merge

### Pipeline Principal (Deployment) 🚀

**¿Cuándo se ejecuta?** Al hacer push a la rama `main`

**¿Qué hace?**
1. **Prepare**: Calcula automáticamente la nueva versión (v1.0.1, v1.0.2, etc.)
2. **Test**: Ejecuta todos los tests
3. **Build**: Construye la imagen Docker con la nueva versión
4. **Security**: Escanea vulnerabilidades (opcional)
5. **Publish**: Sube la imagen a Nexus
6. **Deploy**: Actualiza automáticamente tu servidor EC2
7. **Verify**: Verifica que la aplicación funciona

## 🛠️ Archivos Importantes

```
mi-proyecto/
├── .github/workflows/
│   ├── ci-cd.yml              # 🚀 Pipeline principal
│   └── pr-validation.yml      # 🔍 Validación de PRs
├── docker-compose.prod.yaml   # 🐳 Config de producción
├── Dockerfile                 # 📦 Receta para crear imagen
├── app/                       # 💻 Tu código Python
└── tests/                     # 🧪 Tus tests
```

## 📊 ¿Cómo Ver Que Todo Funciona?

### 1. GitHub Actions
- Ve a tu repo → Actions tab
- Verás una lista de ejecuciones del pipeline
- Click en cualquiera para ver detalles

### 2. Tu Aplicación
```bash
# Verifica que la app funciona
curl http://TU-IP-EC2:8000/health

# Ve la documentación automática
open http://TU-IP-EC2:8000/docs
```

### 3. Métricas (Monitoring)
```bash
# Prometheus (métricas raw)
open http://TU-IP-EC2:9090

# Grafana (dashboards bonitos)
open http://TU-IP-EC2:3000
# Usuario: admin / Password: admin123
```

### 4. Nexus (Tu Registry)
```bash
# Ver imágenes Docker que subiste
open http://TU-IP-EC2:8081
# Usuario: admin / Password: tu-password
```

## 🐛 Problemas Comunes y Soluciones

### ❌ "Pipeline falla en tests"
```bash
# Ejecutar tests localmente para debuggear:
pytest tests/ -v

# Verificar formato:
black --check app/ tests/
```

### ❌ "No se puede conectar a EC2"
```bash
# Verificar SSH:
ssh -i ~/.ssh/tu-key ubuntu@TU-IP-EC2

# Verificar que Docker funciona:
ssh -i ~/.ssh/tu-key ubuntu@TU-IP-EC2 "docker --version"
```

### ❌ "Imagen no se sube a Nexus"
```bash
# Verificar credenciales localmente:
docker login TU-NEXUS-URL:8081 -u admin -p tu-password
```

### ❌ "La aplicación no responde"
```bash
# Ver logs de la aplicación:
ssh -i ~/.ssh/tu-key ubuntu@TU-IP-EC2 "cd ~/app-fastapi && docker-compose logs -f"
```

## 🎓 Conceptos DevOps que Estás Aplicando

### 1. **Continuous Integration (CI)**
- Cada commit ejecuta tests automáticamente
- El código se integra frecuentemente
- Los problemas se detectan temprano

### 2. **Continuous Deployment (CD)**
- Código que pasa tests se despliega automáticamente
- Deployments son consistentes y repetibles
- Menos errores humanos

### 3. **Infrastructure as Code**
- Tu infraestructura se define en archivos (docker-compose.yaml)
- Reproducible en cualquier servidor
- Versionado como código

### 4. **Containerization**
- Tu aplicación corre en contenedores Docker
- Mismo ambiente en desarrollo y producción
- Fácil escalabilidad

### 5. **Monitoring & Observability**
- Métricas en tiempo real con Prometheus
- Visualización con Grafana
- Detectar problemas antes que los usuarios

## 🚀 Próximos Pasos (Opcional)

Si quieres seguir aprendiendo:

1. **Añadir más tests**: Coverage, tests de integración
2. **Mejorar monitoreo**: Alertas, logs centralizados  
3. **Múltiples ambientes**: Staging, desarrollo
4. **Rollback automático**: Si deployment falla
5. **Feature flags**: Activar/desactivar funcionalidades

## 📚 Recursos Adicionales

- [Docker Tutorial](https://docs.docker.com/get-started/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Prometheus Basics](https://prometheus.io/docs/introduction/getting_started/)
- [FastAPI + Docker](https://fastapi.tiangolo.com/deployment/docker/)

## 🎉 ¡Felicidades!

Has implementado un pipeline CI/CD completo. Esto es exactamente lo que usan las empresas en producción. Los conceptos que aplicaste:

- ✅ **Automatización** - Menos trabajo manual
- ✅ **Testing** - Código más confiable  
- ✅ **Deployment** - Releases más rápidos y seguros
- ✅ **Monitoring** - Visibilidad de tu aplicación
- ✅ **DevOps Culture** - Desarrollo y operaciones unidos

**¡Ahora eres un DevOps Engineer junior!** 🎊

---

💡 **Tip para tu presentación final:** Muestra el pipeline funcionando en vivo - haz un cambio pequeño, push, y ve cómo se despliega automáticamente. ¡Es muy impresionante! 