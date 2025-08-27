# 🎯 Rifas Anica - Plataforma Integral de Rifas y Sanes

[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Plataforma web completa para la gestión de rifas y sanes (sistemas de ahorro colaborativo) con funcionalidades avanzadas de administración, pagos y notificaciones.**

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🚀 Demo](#-demo)
- [🛠️ Tecnologías](#️-tecnologías)
- [📦 Instalación](#-instalación)
- [⚙️ Configuración](#️-configuración)
- [🎮 Uso](#-uso)
- [📚 Documentación](#-documentación)
- [🤝 Contribución](#-contribución)
- [📄 Licencia](#-licencia)

## ✨ Características

### 🎲 Gestión de Rifas
- **Creación y administración** de rifas con premios personalizables
- **Cálculos automáticos** de viabilidad y rentabilidad en tiempo real
- **Sistema de tickets** con numeración automática
- **Sorteos automáticos** con selección de ganadores
- **Estados de rifa**: Borrador, Activa, Pausada, Finalizada, Cancelada

### 💰 Gestión de Sanes (Sistemas de Ahorro)
- **Creación de sanes** con parámetros personalizables
- **Cálculos automáticos** de cuotas y fechas sugeridas
- **Asignación automática** de turnos de cobro
- **Seguimiento de pagos** por participante
- **Frecuencias de pago**: Diaria, Semanal, Quincenal, Mensual

### 💳 Sistema de Facturación
- **Generación automática** de facturas para todas las transacciones
- **Sistema de comprobantes** con validación de archivos
- **Estados de pago**: Pendiente, Confirmado, Rechazado, Cancelado
- **Historial completo** de transacciones
- **Exportación** de reportes en PDF y CSV

### 🔔 Sistema de Notificaciones
- **Notificaciones en tiempo real** para eventos importantes
- **Campana de notificaciones** en la interfaz principal
- **Tipos de notificación**: Rifas, Sanes, Pagos, Sistema
- **Marcado de leídas** y gestión de notificaciones

### 👥 Gestión de Usuarios
- **Registro y autenticación** de usuarios
- **Perfiles personalizables** con información detallada
- **Roles de usuario**: Usuario regular, Organizador, Administrador
- **Estadísticas personales** de participación y gastos

### 🛡️ Panel de Administración
- **Dashboard completo** con estadísticas en tiempo real
- **Gestión de usuarios** con búsqueda y filtros
- **Administración de rifas y sanes**
- **Gestión de facturas y pagos**
- **Sistema de logs** para auditoría
- **Reportes financieros** detallados

### 📱 Aplicación Móvil
- **WebView integrado** para acceso móvil
- **Diseño responsivo** optimizado para dispositivos móviles
- **Funcionalidades completas** desde la app móvil

## 🚀 Demo

### Acceso a la Aplicación
- **URL Principal**: `http://127.0.0.1:8000`
- **Panel de Admin**: `http://127.0.0.1:8000/dashboard/`
- **API Endpoints**: `http://127.0.0.1:8000/api/`

### Credenciales de Prueba
```bash
# Superusuario (crear con el comando createsuperuser)
Usuario: admin
Contraseña: admin123

# Usuario de prueba
Usuario: test@example.com
Contraseña: test123
```

## 🛠️ Tecnologías

### Backend
- **Django 5.1.7** - Framework web principal
- **Python 3.10+** - Lenguaje de programación
- **MySQL 8.0+** - Base de datos principal
- **Django REST Framework** - API REST
- **Pillow** - Procesamiento de imágenes
- **ReportLab** - Generación de PDFs

### Frontend
- **Tailwind CSS 3.0** - Framework de estilos
- **JavaScript ES6+** - Interactividad del cliente
- **Alpine.js** - Framework JavaScript ligero
- **Chart.js** - Gráficos y visualizaciones

### Herramientas de Desarrollo
- **Git** - Control de versiones
- **Docker** - Containerización (opcional)
- **Postman** - Testing de APIs
- **MySQL Workbench** - Gestión de base de datos

## 📦 Instalación

### Prerrequisitos

Asegúrate de tener instalado:

- ✅ **Python 3.10** o superior
- ✅ **Git**
- ✅ **MySQL 8.0** o superior
- ✅ **Node.js 16+** (para desarrollo frontend)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/cat507/web-rifas-anica.git
cd web-rifas-anica
```

### 2. Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de Node.js (opcional)
npm install
```

### 4. Configurar Base de Datos

```sql
-- Conectar a MySQL
mysql -u root -p

-- Crear base de datos
CREATE DATABASE anica_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario (opcional)
CREATE USER 'anica_user'@'localhost' IDENTIFIED BY 'anica_password';
GRANT ALL PRIVILEGES ON anica_db.* TO 'anica_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar Variables de Entorno

```bash
# Crear archivo .env
cp .env.example .env

# Editar variables de entorno
nano .env
```

```env
# Configuración de Base de Datos
DB_NAME=anica_db
DB_USER=anica_user
DB_PASSWORD=anica_password
DB_HOST=localhost
DB_PORT=3306

# Configuración de Django
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_de_aplicacion
```

### 6. Aplicar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales (opcional)
python manage.py loaddata initial_data.json
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar el Servidor

```bash
# Servidor de desarrollo
python manage.py runserver

# Servidor para red local (para app móvil)
python manage.py runserver 0.0.0.0:8000
```

## ⚙️ Configuración

### Configuración de Archivos Estáticos

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Configuración de Email

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_password_de_aplicacion'
```

### Configuración de Logs

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🎮 Uso

### Comandos Principales

```bash
# Desarrollo
python manage.py runserver          # Servidor de desarrollo
python manage.py runserver 0.0.0.0:8000  # Servidor para red local

# Base de datos
python manage.py makemigrations     # Crear migraciones
python manage.py migrate            # Aplicar migraciones
python manage.py createsuperuser    # Crear administrador

# Mantenimiento
python manage.py collectstatic      # Recolectar archivos estáticos
python manage.py check              # Verificar configuración
python manage.py shell              # Shell de Django

# Pruebas
python manage.py test               # Ejecutar pruebas
python test_calculations.py         # Pruebas de cálculos
python test_facturas.py             # Pruebas de facturas
```

### Estructura del Proyecto

```
sanes_project/
├── sanes/                     # Aplicación principal
│   ├── models.py             # Modelos de datos
│   ├── views.py              # Vistas y lógica de negocio
│   ├── urls.py               # Configuración de URLs
│   ├── forms.py              # Formularios
│   ├── utils.py              # Utilidades y cálculos
│   └── templates/            # Plantillas HTML
├── static/                   # Archivos estáticos
│   ├── css/                  # Estilos CSS
│   ├── js/                   # JavaScript
│   └── images/               # Imágenes
├── media/                    # Archivos subidos por usuarios
├── requirements.txt          # Dependencias de Python
├── manage.py                # Script de gestión de Django
└── README.md                # Este archivo
```

### Flujo de Trabajo Típico

1. **Crear una Rifa/San**
   - Acceder a "Crear Rifa" o "Crear San"
   - Llenar formulario con parámetros
   - Ver cálculos automáticos de viabilidad
   - Confirmar creación

2. **Gestionar Participantes**
   - Usuarios se inscriben en rifas/sanes
   - Sistema genera facturas automáticamente
   - Usuarios suben comprobantes de pago

3. **Administrar Pagos**
   - Administradores revisan comprobantes
   - Confirman o rechazan pagos
   - Sistema actualiza estados automáticamente

4. **Finalizar Actividades**
   - Rifas: Sorteo automático de ganadores
   - Sanes: Distribución de fondos según turnos

## 📚 Documentación

### Documentación Específica

- 📖 **[Cálculos Automáticos](./sanes_project/CALCULOS_AUTOMATICOS.md)** - Sistema de cálculos en tiempo real
- 💳 **[Sistema de Facturas](./SISTEMA_FACTURAS.md)** - Gestión completa de facturación
- 📱 **[Aplicación Móvil](./README-APP.md)** - Configuración y uso de la app móvil
- 📝 **[Changelog](./CHANGELOG.md)** - Historial de cambios y versiones

### APIs y Endpoints

```bash
# Autenticación
POST /api/auth/login/          # Iniciar sesión
POST /api/auth/logout/         # Cerrar sesión
POST /api/auth/register/       # Registrar usuario

# Rifas
GET    /api/rifas/            # Listar rifas
POST   /api/rifas/            # Crear rifa
GET    /api/rifas/{id}/       # Obtener rifa
PUT    /api/rifas/{id}/       # Actualizar rifa
DELETE /api/rifas/{id}/       # Eliminar rifa

# Sanes
GET    /api/sanes/            # Listar sanes
POST   /api/sanes/            # Crear san
GET    /api/sanes/{id}/       # Obtener san
PUT    /api/sanes/{id}/       # Actualizar san
DELETE /api/sanes/{id}/       # Eliminar san

# Facturas
GET    /api/facturas/         # Listar facturas
POST   /api/facturas/         # Crear factura
GET    /api/facturas/{id}/    # Obtener factura
PUT    /api/facturas/{id}/    # Actualizar factura
```

### Ejemplos de Uso

#### Crear una Rifa

```python
from sanes.models import Rifa
from django.contrib.auth.models import User

# Obtener usuario organizador
organizador = User.objects.get(username='admin')

# Crear rifa
rifa = Rifa.objects.create(
    titulo='Rifa iPhone 15',
    descripcion='Rifa de un iPhone 15 Pro Max',
    premio='iPhone 15 Pro Max 256GB',
    precio_ticket=10.00,
    total_tickets=100,
    organizador=organizador,
    estado='activa'
)
```

#### Crear un San

```python
from sanes.models import San
from datetime import date, timedelta

# Crear san
san = San.objects.create(
    nombre='San Navidad 2024',
    descripcion='San para ahorrar para Navidad',
    precio_total=1000.00,
    total_participantes=10,
    frecuencia_pago='mensual',
    fecha_inicio=date.today(),
    fecha_fin=date.today() + timedelta(days=300),
    organizador=organizador,
    estado='activo'
)
```

## 🤝 Contribución

### Cómo Contribuir

1. **Fork** el repositorio
2. **Clone** tu fork localmente
3. **Crea** una rama para tu feature
4. **Desarrolla** tu feature
5. **Prueba** tu código
6. **Commit** tus cambios
7. **Push** a tu rama
8. **Crea** un Pull Request

### Estándares de Código

```python
# PEP 8 - Estilo de código Python
def calcular_viabilidad_rifa(precio_ticket, total_tickets, valor_premio):
    """
    Calcula la viabilidad de una rifa basada en sus parámetros.
    
    Args:
        precio_ticket (Decimal): Precio por ticket
        total_tickets (int): Número total de tickets
        valor_premio (Decimal): Valor del premio
        
    Returns:
        dict: Diccionario con métricas de viabilidad
    """
    recaudacion_esperada = precio_ticket * total_tickets
    ganancia = recaudacion_esperada - valor_premio
    
    return {
        'viable': ganancia > 0,
        'recaudacion_esperada': recaudacion_esperada,
        'ganancia': ganancia,
        'porcentaje_ganancia': (ganancia / recaudacion_esperada) * 100
    }
```

### Reportar Bugs

Para reportar bugs, usa el sistema de [Issues de GitHub](https://github.com/cat507/web-rifas-anica/issues) e incluye:

- Descripción detallada del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Información del sistema (OS, versión de Python, Django)
- Capturas de pantalla (si aplica)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Soporte

### Contacto

- **Email**: soporte@rifasanica.com
- **Documentación**: [docs.rifasanica.com](https://docs.rifasanica.com)
- **Issues**: [GitHub Issues](https://github.com/cat507/web-rifas-anica/issues)

### Comunidad

- **Discord**: [Servidor de Discord](https://discord.gg/rifasanica)
- **Telegram**: [Canal de Telegram](https://t.me/rifasanica)
- **YouTube**: [Canal de YouTube](https://youtube.com/@rifasanica)

---

<div align="center">

**Desarrollado con ❤️ por el Equipo Rifas Anica**

[![GitHub stars](https://img.shields.io/github/stars/cat507/web-rifas-anica?style=social)](https://github.com/cat507/web-rifas-anica/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/cat507/web-rifas-anica?style=social)](https://github.com/cat507/web-rifas-anica/network/members)
[![GitHub issues](https://img.shields.io/github/issues/cat507/web-rifas-anica)](https://github.com/cat507/web-rifas-anica/issues)

</div>