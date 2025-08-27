# Configuración de Google OAuth con django-allauth

## ✅ Problemas Solucionados

1. **Error de login corregido**: Se solucionó el `AttributeError: 'NoneType' object has no attribute 'method'`
2. **Botón de Google funcional**: Ahora el botón de Google funciona correctamente
3. **Configuración de allauth optimizada**: Se corrigieron todos los warnings de configuración

## 🔧 Configuración Actual

### 1. Dependencias Instaladas
- `django-allauth` ✅
- `reportlab` ✅ (para generar PDFs)

### 2. Configuración en settings.py
- ✅ `ACCOUNT_LOGIN_METHODS = {"username", "email"}`
- ✅ `ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]`
- ✅ `SOCIALACCOUNT_PROVIDERS` configurado para Google
- ✅ Adaptadores personalizados configurados

### 3. Templates Actualizados
- ✅ `login.html` con botón de Google funcional
- ✅ `register.html` con botón de Google funcional
- ✅ Carga de `socialaccount` en ambos templates

## 🚀 Cómo Configurar Google OAuth

### Paso 1: Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google+ 
4. Ve a "Credenciales" → "Crear credenciales" → "ID de cliente de OAuth 2.0"
5. Configura:
   - **Tipo de aplicación**: Aplicación web
   - **Nombre**: Rifas Anica
   - **URI de redirección autorizados**: 
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://127.0.0.1:8000/accounts/google/login/callback/`

### Paso 2: Configurar Variables de Entorno

Crea o actualiza tu archivo `.env`:

```env
# Google OAuth
GOOGLE_CLIENT_ID=tu_client_id_aqui
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
```

### Paso 3: Configurar en Django Admin

1. Ejecuta el servidor: `python manage.py runserver`
2. Ve a `http://localhost:8000/admin/`
3. Inicia sesión con un superusuario
4. Ve a **Sites** y asegúrate de que el dominio sea `localhost:8000`
5. Ve a **Social Applications** → **Add social application**
6. Configura:
   - **Provider**: Google
   - **Name**: Google
   - **Client ID**: Tu Client ID de Google
   - **Secret key**: Tu Client Secret de Google
   - **Sites**: Selecciona `localhost:8000`

### Paso 4: Probar la Funcionalidad

1. Ve a `http://localhost:8000/accounts/login/`
2. Haz clic en "Continuar con Google"
3. Deberías ser redirigido a Google para autenticación
4. Después de autenticarte, serás redirigido de vuelta a tu aplicación

## 🔄 Script de Configuración Automática

Si tienes las variables de entorno configuradas, puedes ejecutar:

```bash
python manage.py shell < scripts/setup_google_oauth.py
```

Este script configurará automáticamente:
- El sitio en Django
- La aplicación social de Google
- Las credenciales de OAuth

## 📝 Archivos Modificados

### Settings
- `sanes_project/settings.py` - Configuración de allauth y Google OAuth

### Forms
- `sanes/forms.py` - CustomLoginForm corregido

### Templates
- `sanes/templates/account/login.html` - Botón de Google funcional
- `sanes/templates/account/register.html` - Botón de Google funcional

### Nuevos Archivos
- `sanes/adapters.py` - Adaptadores personalizados para allauth
- `scripts/setup_google_oauth.py` - Script de configuración automática

## 🎯 Funcionalidades Implementadas

1. **Login con Google**: Los usuarios pueden iniciar sesión con sus cuentas de Google
2. **Registro con Google**: Los usuarios pueden registrarse con Google
3. **Mapeo automático de datos**: 
   - Nombre y apellido del perfil de Google
   - Email de Google
   - Foto de perfil de Google
   - Username único basado en el email

## 🔒 Seguridad

- Las credenciales se almacenan de forma segura en variables de entorno
- Solo se solicitan los permisos necesarios (email y perfil)
- Los usuarios pueden desconectar sus cuentas de Google desde el admin

## 🐛 Solución de Problemas

### Error: "No se pudo autenticar con Google"
- Verifica que las credenciales de Google sean correctas
- Asegúrate de que las URIs de redirección estén configuradas correctamente
- Verifica que la API de Google+ esté habilitada

### Error: "Sitio no encontrado"
- Ve al admin de Django y verifica que el sitio esté configurado
- El dominio debe ser `localhost:8000` para desarrollo

### Error: "Client ID no válido"
- Verifica que el Client ID y Client Secret estén correctos
- Asegúrate de que la aplicación esté asociada al sitio correcto

## 📞 Soporte

Si tienes problemas con la configuración:
1. Verifica que todas las dependencias estén instaladas
2. Revisa los logs del servidor para errores específicos
3. Asegúrate de que las credenciales de Google sean válidas

