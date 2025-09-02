# 🎯 SANes & Rifas - Aplicación Móvil

Aplicación móvil React Native para la gestión de SANes (Sociedades de Ahorro y Negocio) y rifas, replicando toda la funcionalidad del backend Django web.

## 📱 Características Principales

### 🔐 Autenticación
- Registro de usuarios con validaciones
- Inicio de sesión seguro
- Gestión de tokens de autenticación

### 🏠 Pantalla Principal
- Listado de SANes activos
- Listado de rifas disponibles
- Filtros por monto, frecuencia y plazas
- Navegación intuitiva

### 📊 Detalles de SAN
- Información completa del SAN
- Visualización de turnos y pagos
- Historial de contribuciones
- Sistema de comentarios
- Botón para unirse al SAN

### 🎫 Detalles de Rifa
- Información de la rifa
- Compra de tickets con modal de selección
- Historial de tickets comprados
- Sistema de comentarios

### 💳 Sistema de Pagos
- Pagos digitales simulados (tarjeta, PayPal, Nequi)
- Pagos en efectivo con referencias
- Subida de comprobantes
- Estados de pago (Pendiente → Validado → Rechazado)

### 👤 Perfil de Usuario
- Información personal editable
- Estadísticas de participación
- Historial de SANes y rifas
- Gestión de facturas

### 💬 Sistema de Comentarios
- Comentarios en SANes y rifas
- Respuestas anidadas
- Moderación de contenido
- Auditoría completa

### 🔔 Notificaciones
- Notificaciones de pagos
- Alertas de turnos
- Mensajes del administrador
- Filtros por estado

## 🛠️ Tecnologías Utilizadas

- **React Native** - Framework móvil
- **TypeScript** - Tipado estático
- **React Navigation** - Navegación entre pantallas
- **React Context API** - Gestión de estado global
- **Axios** - Cliente HTTP
- **AsyncStorage** - Almacenamiento local
- **React Native Vector Icons** - Iconografía

## 📋 Requisitos Previos

- Node.js (versión 18 o superior)
- npm o yarn
- React Native CLI
- Android Studio (para desarrollo Android)
- JDK 11 o superior
- Android SDK

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd app_project_sanes
```

### 2. Instalar dependencias
```bash
npm install
# o
yarn install
```

### 3. Configurar variables de entorno
Crear un archivo `.env` en la raíz del proyecto:
```env
API_BASE_URL=http://192.168.1.106:8000
```

### 4. Configurar Android
Asegúrate de que las variables de entorno estén configuradas:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### 5. Ejecutar en Android
```bash
# Iniciar Metro bundler
npm start

# En otra terminal, ejecutar la app
npm run android
```

## 📱 Estructura del Proyecto

```
src/
├── contexts/          # Contextos de React (AuthContext)
├── navigation/        # Configuración de navegación
├── screens/          # Pantallas de la aplicación
├── services/         # Servicios de API y utilidades
└── types/            # Definiciones de TypeScript
```

## 🔧 Scripts Disponibles

- `npm start` - Inicia Metro bundler
- `npm run android` - Ejecuta la app en Android
- `npm run ios` - Ejecuta la app en iOS
- `npm run build:android` - Construye APK de release
- `npm run build:apk` - Construye APK de debug

## 📱 Pantallas Implementadas

1. **LoginScreen** - Inicio de sesión
2. **RegisterScreen** - Registro de usuarios
3. **HomeScreen** - Pantalla principal con listados
4. **SanDetailScreen** - Detalle de SAN
5. **RifaDetailScreen** - Detalle de rifa
6. **ProfileScreen** - Perfil del usuario
7. **NotificationsScreen** - Notificaciones
8. **CommentsScreen** - Sistema de comentarios
9. **PaymentScreen** - Procesamiento de pagos

## 🔌 Integración con Backend

La aplicación se conecta con el backend Django a través de APIs REST:

- **Autenticación**: `/api/auth/login/`, `/api/auth/register/`
- **SANes**: `/api/sanes/`, `/api/sanes/{id}/`
- **Rifas**: `/api/rifas/`, `/api/rifas/{id}/`
- **Pagos**: `/api/pagos/`, `/api/pagos/{id}/`
- **Comentarios**: `/api/comentarios/`
- **Notificaciones**: `/api/notificaciones/`

## 🎨 Diseño y UX

- **Mobile-first**: Diseño optimizado para dispositivos móviles
- **Consistencia visual**: Paleta de colores y tipografía uniforme
- **Navegación intuitiva**: Bottom tabs y navegación por stack
- **Feedback visual**: Estados de carga, errores y éxito
- **Accesibilidad**: Contraste adecuado y tamaños de texto legibles

## 🔒 Seguridad

- **Autenticación JWT**: Tokens seguros para sesiones
- **Validación de formularios**: Validación tanto en cliente como servidor
- **Sanitización de datos**: Prevención de inyección de código
- **Almacenamiento seguro**: Tokens en AsyncStorage con encriptación

## 📊 Estado de la Aplicación

La aplicación mantiene el estado global a través de:

- **AuthContext**: Estado de autenticación del usuario
- **AsyncStorage**: Persistencia de datos locales
- **API Service**: Comunicación con el backend
- **React Navigation**: Estado de navegación

## 🚀 Despliegue

### Generar APK de Release
```bash
cd android
./gradlew assembleRelease
```

El APK se generará en: `android/app/build/outputs/apk/release/app-release.apk`

### Generar Bundle de Release
```bash
cd android
./gradlew bundleRelease
```

## 🐛 Solución de Problemas

### Error de Metro
```bash
npm start --reset-cache
```

### Error de Gradle
```bash
cd android
./gradlew clean
```

### Error de Dependencias
```bash
rm -rf node_modules
npm install
```

## 📝 Notas de Desarrollo

- La aplicación está configurada para conectarse a `http://192.168.1.106:8000`
- Todos los pagos son simulados para fines de demostración
- Las notificaciones se simulan localmente si el backend no está disponible
- La aplicación incluye manejo de errores robusto y estados de carga

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación del backend Django

---

**Desarrollado con ❤️ para la comunidad de SANes y Rifas**
