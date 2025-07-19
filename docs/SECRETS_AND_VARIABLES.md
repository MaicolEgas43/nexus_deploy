# 🔐 Configuración de Secrets y Variables - Guía Simple

## 📋 ¿Qué son Secrets y Variables?

**Secrets** 🔒 = Información sensible (passwords, API keys, SSH keys)  
**Variables** 📊 = Configuración no sensible (URLs, puertos, nombres)

## 🔑 Secrets Requeridos

Configura estos en: `Repositorio → Settings → Secrets and variables → Actions → Secrets`

| Secret | ¿Qué es? | Ejemplo | ¿Dónde obtenerlo? |
|--------|----------|---------|-------------------|
| `NEXUS_USERNAME` | Usuario de Nexus | `admin` | Al configurar Nexus |
| `NEXUS_PASSWORD` | Password de Nexus | `mi-password-123` | Al configurar Nexus |
| `EC2_SSH_KEY` | Clave SSH privada | `-----BEGIN RSA...` | Generada con `ssh-keygen` |
| `EC2_HOST` | IP de tu servidor | `54.123.45.67` | Consola de AWS EC2 |
| `EC2_USER` | Usuario SSH | `ubuntu` | Por defecto en Ubuntu |

## 📊 Variables Requeridas

Configura estas en: `Repositorio → Settings → Secrets and variables → Actions → Variables`

| Variable | ¿Qué es? | Ejemplo | ¿Para qué? |
|----------|----------|---------|------------|
| `NEXUS_URL` | URL de Nexus | `http://ec2-13-223-57-61.compute-1.amazonaws.com` | Conectar a Nexus |
| `NEXUS_DOCKER_PORT` | Puerto Docker | `8081` | Subir imágenes |
| `ENABLE_SECURITY_SCAN` | ¿Escanear seguridad? | `true` | Activar/desactivar Trivy |

## 🛠️ Configuración Paso a Paso

### Paso 1: SSH Key para EC2

```bash
# Generar nueva SSH key (si no tienes)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/devops-key

# Copiar key pública al EC2
ssh-copy-id -i ~/.ssh/devops-key.pub ubuntu@TU-IP-EC2

# Ver la key privada (para copiar al secret)
cat ~/.ssh/devops-key
```

### Paso 2: Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. `Settings` → `Secrets and variables` → `Actions`
3. Click `New repository secret`
4. Añade cada secret de la tabla:

```
NEXUS_USERNAME = admin
NEXUS_PASSWORD = tu-password-nexus
EC2_SSH_KEY = (pegar contenido de ~/.ssh/devops-key)
EC2_HOST = 54.123.45.67
EC2_USER = ubuntu
```

### Paso 3: Configurar Variables en GitHub

1. En la misma página, click pestaña `Variables`
2. Click `New repository variable`
3. Añade cada variable:

```
NEXUS_URL = http://tu-nexus-server.com
NEXUS_DOCKER_PORT = 8081
ENABLE_SECURITY_SCAN = true
```

## ✅ Script de Verificación

Guarda esto como `verify-config.sh` y ejecútalo:

```bash
#!/bin/bash
echo "🔍 Verificando configuración..."

# Verificar conexión SSH a EC2
echo "📡 Probando SSH a EC2..."
ssh -i ~/.ssh/devops-key -o ConnectTimeout=5 ubuntu@$EC2_HOST "echo '✅ SSH OK'" || echo "❌ SSH falló"

# Verificar Docker en EC2
echo "🐳 Verificando Docker en EC2..."
ssh -i ~/.ssh/devops-key ubuntu@$EC2_HOST "docker --version" || echo "❌ Docker no encontrado"

# Verificar Nexus
echo "📦 Probando conexión a Nexus..."
curl -f -s "$NEXUS_URL:$NEXUS_DOCKER_PORT" && echo "✅ Nexus accesible" || echo "❌ Nexus no accesible"

echo "✨ Verificación completada"
```

## 🚨 Problemas Comunes

### ❌ "Secret EC2_SSH_KEY no funciona"

**Problema:** La key SSH no tiene el formato correcto

**Solución:**
```bash
# La key debe verse así:
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA7Z8...
(muchas líneas)
...8XyZ==
-----END RSA PRIVATE KEY-----

# Verificar que es privada (no pública):
head -1 ~/.ssh/devops-key
# Debe decir "BEGIN RSA PRIVATE KEY", no "BEGIN PUBLIC KEY"
```

### ❌ "No puedo conectar a EC2"

**Problema:** IP incorrecta o security group

**Solución:**
```bash
# Verificar IP de EC2 en AWS Console
# Verificar Security Group permite SSH (puerto 22)
# Probar conexión manual:
ssh -i ~/.ssh/devops-key ubuntu@TU-IP-EC2
```

### ❌ "Nexus no responde"

**Problema:** Nexus no está corriendo o puerto cerrado

**Solución:**
```bash
# En el servidor de Nexus:
docker ps | grep nexus
curl http://localhost:8081

# Verificar puerto 8081 en security group
```

## 💡 Tips de Seguridad

### ✅ Buenas Prácticas

1. **Nunca compartir secrets**: Cada persona debe tener sus propios
2. **SSH keys únicas**: Una key por proyecto/ambiente
3. **Passwords fuertes**: Mínimo 12 caracteres
4. **Rotar credenciales**: Cambiar passwords regularmente

### ❌ Errores Comunes

1. **No commitear secrets en código**: GitHub detecta passwords y los revoca
2. **No usar echo con secrets**: Los logs son públicos
3. **No hardcodear passwords**: Usar variables siempre

## 📋 Checklist Final

Antes de hacer tu primer deployment:

- [ ] ✅ Todos los secrets configurados en GitHub
- [ ] ✅ Todas las variables configuradas en GitHub  
- [ ] ✅ SSH funciona desde tu máquina a EC2
- [ ] ✅ Docker instalado y funcionando en EC2
- [ ] ✅ Nexus accesible desde internet
- [ ] ✅ Security groups permiten puertos 22, 8000, 8081, 9090, 3000

## 🎓 Para Tu Presentación

**Muestra esto en tu demo:**

1. Cambiar un secret en GitHub Settings
2. Mostrar que no aparece en los logs del pipeline
3. Explicar por qué separamos secrets de variables
4. Demostrar que el pipeline falla si faltan secrets

---

**💡 Recuerda:** Los secrets son la parte más importante de la seguridad en DevOps. ¡Manéjalos con cuidado! 