# Instrucciones para Configurar y Ejecutar la App Móvil

Este archivo contiene las instrucciones necesarias para configurar y ejecutar la aplicación móvil de "Rifa Anica" en un dispositivo o emulador, así como para solucionar posibles problemas durante la configuración.

## Requisitos Previos

### Requisitos para el Backend (Django)

Asegúrate de que el backend (Django) esté corriendo antes de intentar ejecutar la app móvil. Para configurarlo:

1. **Clonar el repositorio y configurar el entorno del backend**:
    - Clona el repositorio: `git clone <url-del-repositorio>`
    - Navega a la carpeta del backend: `cd backend`
    - Crea y activa un entorno virtual:

        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    - Instala las dependencias:

        ```bash
        pip install -r requirements.txt
        ```

2. **Configurar el servidor Django**:
    - Para que la app móvil se conecte al servidor desde un dispositivo o emulador, necesitas que Django escuche en todas las interfaces de red. Para ello, corre el siguiente comando:

        ```bash
        python manage.py runserver 0.0.0.0:8000
        ```

    - Esto permitirá que el servidor esté disponible en la IP local de tu máquina (por ejemplo: `http://192.168.1.106:8000`).

3. **Comprobación**:
    - Abre un navegador en tu PC y asegúrate de que puedes acceder a la aplicación a través de `http://127.0.0.1:8000` o `http://<tu-ip-local>:8000`.

---

## Requisitos para el Frontend (App Móvil)

### Instalación de dependencias

1. **Clonar el repositorio y configurar el entorno del frontend**:
    - Clona el repositorio y navega a la carpeta del frontend:

        ```bash
        git clone <url-del-repositorio>
        cd frontend
        ```

    - Instala las dependencias necesarias:

        ```bash
        npm install
        ```

2. **Verifica la conexión con el backend**:
    - Asegúrate de que el servidor Django esté corriendo correctamente.
    - En el archivo `App.js` de la app móvil, configura la URL correcta para el WebView. En lugar de usar `localhost`, utiliza la IP de la red local del servidor Django, por ejemplo:

        ```js
        <WebView source={{ uri: 'http://192.168.1.106:8000' }} />
        ```

    - Esto asegura que la app pueda conectarse al servidor Django desde otro dispositivo o emulador en la misma red.

---

## Pasos para Ejecutar la App en un Emulador o Dispositivo

1. **Asegúrate de que ambos dispositivos estén en la misma red local**.
2. **Ejecutar la app en un emulador Android**:
    - Si usas Android Studio, abre el emulador y ejecuta el siguiente comando para iniciar la app:

        ```bash
        npx react-native run-android
        ```

    - Si usas otro emulador, asegúrate de que está configurado para acceder a la misma red.

3. **Ejecutar la app en un dispositivo físico**:
    - Conecta el dispositivo físico al ordenador y ejecuta el siguiente comando:

        ```bash
        npx react-native run-android
        ```

4. **Verificar la conexión en la app**:
    - Al abrir la app, el WebView debe cargar la página desde la URL configurada en el código (`http://<tu-ip-local>:8000`).

---

## Errores Comunes y Soluciones

### 1. **Error `ERR_CONNECTION_REFUSED` al intentar cargar la página**:
- **Problema**: Este error ocurre cuando el WebView no puede conectarse al servidor Django.
- **Solución**: Asegúrate de que Django esté configurado para escuchar en todas las interfaces (`0.0.0.0`) y que el servidor esté corriendo en la IP correcta. Ejemplo:

    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

    También, revisa que el WebView esté apuntando a la IP local correcta en `App.js`.

### 2. **Problemas con la conexión en el emulador**:
- **Problema**: Los emuladores pueden tener problemas para conectarse a servidores en la red local.
- **Solución**: Si estás utilizando un emulador, verifica que está en la misma red Wi-Fi que tu PC. También puedes intentar usar la dirección IP de la máquina como `10.0.2.2` en lugar de la IP local (`192.168.x.x`).

### 3. **La app no se carga o tarda mucho**:
- **Problema**: Esto puede ser causado por una alta carga en el servidor o un problema en el emulador.
- **Solución**: Asegúrate de que el servidor Django esté optimizado para manejar múltiples solicitudes. Si es posible, intenta probar en un dispositivo físico para ver si el problema persiste.

---

## Configuración para Nuevas Máquinas

### 1. **Backend (Django)**:
- Clona el repositorio y sigue los pasos en la sección de "Requisitos para el Backend".
- Asegúrate de configurar el servidor Django correctamente para que se escuche en todas las interfaces de red.

### 2. **Frontend (App Móvil)**:
- Clona el repositorio y sigue los pasos en la sección de "Requisitos para el Frontend".
- Actualiza la URL del WebView con la IP de la máquina donde está corriendo el servidor Django.

---

## Conclusión

¡Ahora deberías tener todo configurado correctamente! Si encuentras algún problema, revisa los errores comunes y sus soluciones, o consulta el [changelog](./CHANGELOG.md) para obtener más información sobre las últimas actualizaciones.

