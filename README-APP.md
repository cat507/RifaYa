# 📱 Aplicación Móvil - Rifas Anica

> **Guía completa para configurar, ejecutar y mantener la aplicación móvil de Rifas Anica**

## 📋 Tabla de Contenidos

- [🎯 Descripción General](#-descripción-general)
- [📱 Características de la App](#-características-de-la-app)
- [🛠️ Requisitos del Sistema](#️-requisitos-del-sistema)
- [⚙️ Configuración del Backend](#️-configuración-del-backend)
- [📱 Configuración de la App Móvil](#-configuración-de-la-app-móvil)
- [🚀 Ejecución y Pruebas](#-ejecución-y-pruebas)
- [🔧 Solución de Problemas](#-solución-de-problemas)
- [📊 Monitoreo y Logs](#-monitoreo-y-logs)
- [🔄 Actualizaciones](#-actualizaciones)

## 🎯 Descripción General

La aplicación móvil de Rifas Anica es una **WebView integrada** que proporciona acceso completo a la plataforma web desde dispositivos móviles. Utiliza React Native para el contenedor nativo y Django como backend web.

### Arquitectura

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   App Móvil     │ ◄──────────────► │  Servidor Django │
│  (React Native) │                  │   (Backend)     │
│                 │                  │                 │
│ ┌─────────────┐ │                  │ ┌─────────────┐ │
│ │   WebView   │ │                  │ │   Django    │ │
│ │             │ │                  │ │   Views     │ │
│ │  HTML/CSS/  │ │                  │ │             │ │
│ │ JavaScript  │ │                  │ │  Templates  │ │
│ └─────────────┘ │                  │ └─────────────┘ │
└─────────────────┘                  └─────────────────┘
```

## 📱 Características de la App

### ✅ Funcionalidades Completas
- **Acceso total** a todas las funcionalidades de la plataforma web
- **Diseño responsivo** optimizado para pantallas táctiles
- **Navegación nativa** con gestos móviles
- **Notificaciones push** (configuración opcional)
- **Modo offline** para contenido cacheado

### 🎨 Interfaz de Usuario
- **Diseño adaptativo** que se ajusta a diferentes tamaños de pantalla
- **Navegación intuitiva** con menús optimizados para móvil
- **Formularios táctiles** con validación en tiempo real
- **Indicadores de carga** y feedback visual

### 🔒 Seguridad
- **Autenticación segura** con tokens JWT
- **Cifrado HTTPS** para todas las comunicaciones
- **Validación de certificados** SSL
- **Almacenamiento seguro** de credenciales

## 🛠️ Requisitos del Sistema

### Para Desarrollo

#### Backend (Django)
- ✅ **Python 3.10+**
- ✅ **Django 5.1.7+**
- ✅ **MySQL 8.0+**
- ✅ **Node.js 16+** (para herramientas de desarrollo)

#### Frontend (React Native)
- ✅ **Node.js 16+**
- ✅ **npm 8+** o **yarn 1.22+**
- ✅ **React Native CLI**
- ✅ **Android Studio** (para desarrollo Android)
- ✅ **Xcode** (para desarrollo iOS, solo macOS)

### Para Producción

#### Servidor
- ✅ **Ubuntu 20.04+** o **CentOS 8+**
- ✅ **4GB RAM** mínimo
- ✅ **20GB** espacio en disco
- ✅ **Python 3.10+**
- ✅ **MySQL 8.0+**
- ✅ **Nginx** (proxy reverso)

#### Dispositivos Móviles
- ✅ **Android 8.0+** (API level 26+)
- ✅ **iOS 12.0+**
- ✅ **2GB RAM** mínimo
- ✅ **Conexión a internet** estable

## ⚙️ Configuración del Backend

### 1. Preparar el Servidor Django

```bash
# Clonar el repositorio
git clone https://github.com/cat507/web-rifas-anica.git
cd web-rifas-anica

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Base de Datos

```sql
-- Conectar a MySQL
mysql -u root -p

-- Crear base de datos
CREATE DATABASE anica_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario para la aplicación
CREATE USER 'anica_app'@'localhost' IDENTIFIED BY 'anica_password_2024';
GRANT ALL PRIVILEGES ON anica_db.* TO 'anica_app'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configurar Variables de Entorno

```bash
# Crear archivo .env
cp .env.example .env

# Editar configuración
nano .env
```

```env
# Configuración de Base de Datos
DB_NAME=anica_db
DB_USER=anica_app
DB_PASSWORD=anica_password_2024
DB_HOST=localhost
DB_PORT=3306

# Configuración de Django
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu_ip_local,tu_dominio.com

# Configuración para App Móvil
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=True
```

### 4. Aplicar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 5. Configurar Servidor para Red Local

```bash
# Servidor para desarrollo local
python manage.py runserver 0.0.0.0:8000

# O para producción con Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 sanes_project.wsgi:application
```

### 6. Configurar Nginx (Opcional, para Producción)

```nginx
# /etc/nginx/sites-available/anica
server {
    listen 80;
    server_name tu_dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /ruta/a/tu/proyecto/staticfiles/;
    }

    location /media/ {
        alias /ruta/a/tu/proyecto/media/;
    }
}
```

## 📱 Configuración de la App Móvil

### 1. Preparar Entorno de Desarrollo

```bash
# Instalar React Native CLI
npm install -g @react-native-community/cli

# Verificar instalación
npx react-native --version
```

### 2. Configurar Android Studio

```bash
# Configurar variables de entorno
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### 3. Crear Proyecto React Native

```bash
# Crear nuevo proyecto
npx react-native init RifasAnicaApp --template react-native-template-typescript

# Navegar al proyecto
cd RifasAnicaApp

# Instalar dependencias
npm install
```

### 4. Configurar WebView

```bash
# Instalar react-native-webview
npm install react-native-webview

# Para iOS (si estás en macOS)
cd ios && pod install && cd ..
```

### 5. Configurar App.js

```javascript
// App.js
import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  View,
  Text,
  ActivityIndicator,
} from 'react-native';
import { WebView } from 'react-native-webview';

const App = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  // URL del servidor Django
  const SERVER_URL = 'http://192.168.1.100:8000'; // Cambiar por tu IP

  const handleLoadStart = () => {
    setIsLoading(true);
    setHasError(false);
  };

  const handleLoadEnd = () => {
    setIsLoading(false);
  };

  const handleError = (syntheticEvent) => {
    const { nativeEvent } = syntheticEvent;
    console.warn('WebView error: ', nativeEvent);
    setHasError(true);
    setIsLoading(false);
  };

  const renderLoading = () => (
    <View style={styles.loadingContainer}>
      <ActivityIndicator size="large" color="#e92932" />
      <Text style={styles.loadingText}>Cargando Rifas Anica...</Text>
    </View>
  );

  const renderError = () => (
    <View style={styles.errorContainer}>
      <Text style={styles.errorTitle}>Error de Conexión</Text>
      <Text style={styles.errorText}>
        No se pudo conectar al servidor. Verifica que:
      </Text>
      <Text style={styles.errorText}>
        • El servidor Django esté ejecutándose
      </Text>
      <Text style={styles.errorText}>
        • La IP del servidor sea correcta
      </Text>
      <Text style={styles.errorText}>
        • Ambos dispositivos estén en la misma red
      </Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#fcf8f8" />
      
      {hasError ? (
        renderError()
      ) : (
        <WebView
          source={{ uri: SERVER_URL }}
          style={styles.webview}
          onLoadStart={handleLoadStart}
          onLoadEnd={handleLoadEnd}
          onError={handleError}
          javaScriptEnabled={true}
          domStorageEnabled={true}
          startInLoadingState={true}
          scalesPageToFit={true}
          allowsInlineMediaPlayback={true}
          mediaPlaybackRequiresUserAction={false}
          userAgent="RifasAnicaApp/1.0"
        />
      )}
      
      {isLoading && !hasError && renderLoading()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fcf8f8',
  },
  webview: {
    flex: 1,
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fcf8f8',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#1b0e0e',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fcf8f8',
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#e92932',
    marginBottom: 20,
  },
  errorText: {
    fontSize: 14,
    color: '#1b0e0e',
    textAlign: 'center',
    marginBottom: 5,
  },
});

export default App;
```

### 6. Configurar Android

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        android:name=".MainApplication"
        android:label="@string/app_name"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:allowBackup="false"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true">
        
        <activity
            android:name=".MainActivity"
            android:label="@string/app_name"
            android:configChanges="keyboard|keyboardHidden|orientation|screenSize|uiMode"
            android:launchMode="singleTask"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### 7. Configurar iOS (macOS)

```xml
<!-- ios/RifasAnicaApp/Info.plist -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>192.168.1.100</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

## 🚀 Ejecución y Pruebas

### 1. Ejecutar en Emulador Android

```bash
# Iniciar emulador Android
emulator -avd Pixel_4_API_30

# Ejecutar aplicación
npx react-native run-android
```

### 2. Ejecutar en Dispositivo Físico Android

```bash
# Conectar dispositivo via USB
adb devices

# Habilitar depuración USB en el dispositivo
# Configuración > Opciones de desarrollador > Depuración USB

# Ejecutar aplicación
npx react-native run-android
```

### 3. Ejecutar en Simulador iOS (macOS)

```bash
# Abrir simulador iOS
open -a Simulator

# Ejecutar aplicación
npx react-native run-ios
```

### 4. Ejecutar en Dispositivo iOS (macOS)

```bash
# Conectar dispositivo iOS
# Abrir Xcode y configurar certificados de desarrollo

# Ejecutar aplicación
npx react-native run-ios --device "iPhone de Daniel"
```

### 5. Verificar Conexión

```bash
# Verificar que el servidor Django esté ejecutándose
curl http://192.168.1.100:8000

# Verificar conectividad desde el dispositivo
adb shell ping 192.168.1.100
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. Error `ERR_CONNECTION_REFUSED`

**Síntomas**: La app muestra "Error de Conexión" y no puede cargar la página.

**Soluciones**:
```bash
# Verificar que Django esté ejecutándose
ps aux | grep python

# Verificar puerto
netstat -tulpn | grep :8000

# Reiniciar servidor Django
python manage.py runserver 0.0.0.0:8000

# Verificar firewall
sudo ufw status
sudo ufw allow 8000
```

#### 2. Error `ERR_NAME_NOT_RESOLVED`

**Síntomas**: La app no puede resolver el nombre del servidor.

**Soluciones**:
```bash
# Usar IP directa en lugar de nombre de dominio
# Cambiar en App.js:
const SERVER_URL = 'http://192.168.1.100:8000';

# Verificar DNS
nslookup tu_dominio.com

# Usar IP local del servidor
ifconfig  # Linux/macOS
ipconfig  # Windows
```

#### 3. Error de Certificado SSL

**Síntomas**: La app muestra error de certificado no válido.

**Soluciones**:
```javascript
// En App.js, agregar configuración para desarrollo
<WebView
  source={{ uri: SERVER_URL }}
  onShouldStartLoadWithRequest={(request) => {
    // Permitir todas las URLs en desarrollo
    return true;
  }}
  // ... otras props
/>
```

#### 4. Problemas de Rendimiento

**Síntomas**: La app es lenta o se congela.

**Soluciones**:
```javascript
// Optimizar WebView
<WebView
  source={{ uri: SERVER_URL }}
  cacheEnabled={true}
  cacheMode="LOAD_DEFAULT"
  domStorageEnabled={true}
  javaScriptEnabled={true}
  // ... otras props
/>
```

### Debugging Avanzado

#### 1. Habilitar Debug de WebView

```javascript
// En App.js
<WebView
  source={{ uri: SERVER_URL }}
  onMessage={(event) => {
    console.log('WebView message:', event.nativeEvent.data);
  }}
  injectedJavaScript={`
    console.log = function(message) {
      window.ReactNativeWebView.postMessage(message);
    };
  `}
/>
```

#### 2. Logs de React Native

```bash
# Ver logs en tiempo real
npx react-native log-android  # Android
npx react-native log-ios      # iOS

# Limpiar cache
npx react-native start --reset-cache
```

#### 3. Debug de Red

```bash
# Usar Charles Proxy o Fiddler para interceptar tráfico
# Configurar proxy en el dispositivo

# Verificar conectividad
adb shell ping 192.168.1.100
adb shell curl http://192.168.1.100:8000
```

## 📊 Monitoreo y Logs

### 1. Configurar Logs de Django

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'mobile_app.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'sanes.views': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### 2. Monitoreo de Rendimiento

```javascript
// En App.js
import { PerformanceObserver } from 'react-native';

// Monitorear rendimiento
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach((entry) => {
    console.log(`${entry.name}: ${entry.duration}ms`);
  });
});

observer.observe({ entryTypes: ['measure'] });
```

### 3. Métricas de Uso

```python
# views.py
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def log_mobile_access(request):
    """Registrar acceso desde app móvil"""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if 'RifasAnicaApp' in user_agent:
        logger.info(f'Mobile app access: {request.user} at {timezone.now()}')
```

## 🔄 Actualizaciones

### 1. Actualizar Backend

```bash
# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Reiniciar servidor
sudo systemctl restart anica-django
```

### 2. Actualizar App Móvil

```bash
# Actualizar dependencias
npm update

# Limpiar cache
npx react-native start --reset-cache

# Reconstruir aplicación
npx react-native run-android --variant=release
npx react-native run-ios --configuration=Release
```

### 3. Despliegue Automático

```yaml
# .github/workflows/mobile-deploy.yml
name: Mobile App Deployment

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm install
      - name: Build Android APK
        run: npx react-native run-android --variant=release
      - name: Upload APK
        uses: actions/upload-artifact@v2
        with:
          name: app-release
          path: android/app/build/outputs/apk/release/
```

---

## 📞 Soporte

### Recursos Adicionales

- **Documentación React Native**: [reactnative.dev](https://reactnative.dev/)
- **Documentación WebView**: [github.com/react-native-webview](https://github.com/react-native-webview/react-native-webview)
- **Comunidad Django**: [djangoproject.com/community](https://www.djangoproject.com/community/)

### Contacto

- **Email**: soporte@rifasanica.com
- **Issues**: [GitHub Issues](https://github.com/cat507/web-rifas-anica/issues)
- **Discord**: [Servidor de Discord](https://discord.gg/rifasanica)

---

**Versión**: 1.0.0  
**Última actualización**: Agosto 2025  
**Desarrollado por**: Equipo Rifas Anica

