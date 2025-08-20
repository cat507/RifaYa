# Changelog

## [1.0.0] - 2025-03-19
### Añadido
- Se añadió un WebView para la app React Native que accede a la plataforma Django.
- Se solucionó el error de conexión entre la app y el servidor local al modificar la IP a la de la red local.

### Corregido
- Solucionado el problema `ERR_CONNECTION_REFUSED` al hacer que el servidor de Django escuche en `0.0.0.0`.
- Corregido el problema de alta carga de recursos durante la exportación de la APK.

### Notas
- Para hacer funcionar la app en otra máquina, asegúrate de que el servidor de Django esté configurado para escuchar en la red local: `python manage.py runserver 0.0.0.0:8000`.
- Si estás en un emulador o dispositivo físico, asegúrate de que ambos estén en la misma red Wi-Fi.

## [20/03/2025] - [1.0.0]

### Cambios importantes:
- Actualización de `.gitignore` para excluir más archivos y directorios relacionados con React, Xcode, Android, Node.js y otros entornos de desarrollo.
- Eliminación de todos los archivos que fueron previamente ignorados por `.gitignore` pero que ya estaban en el repositorio. Estos archivos fueron eliminados de la caché de Git, asegurando que no se sigan subiendo al repositorio.

### Detalles:
- Se actualizaron las reglas en `.gitignore` para mejorar la gestión de archivos temporales y específicos del entorno de desarrollo (como `node_modules/`, `build/`, `DerivedData/`, etc.).
- Se eliminaron los archivos ya ignorados del repositorio utilizando el comando `git rm -r --cached .` para garantizar que no haya archivos innecesarios en el historial de Git.
- Los archivos eliminados continúan existiendo en el entorno local, pero ya no se rastrean ni se suben al repositorio.
