# **Web para Rifas Anica**  
Proyecto basado en **Django** con **MySQL** como base de datos.

---

## Documentación

- [Instrucciones para la App Móvil](./README-APP.md)

## **📌 Requisitos previos**
Antes de empezar, asegúrate de tener instalado:  
✅ **Python** (versión 3.10 o superior)  
✅ **Git**  
✅ **MySQL**  

Si no los tienes, descárgalos desde aquí:  
🔹 Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
🔹 Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)  
🔹 MySQL: [https://dev.mysql.com/downloads/](https://dev.mysql.com/downloads/)

---

## **Instalación paso a paso**  

### **1️⃣ Clonar el repositorio**  
Abre una terminal y ejecuta:

```sh
git clone https://github.com/cat507/web-rifas-anica.git
```

Luego, entra a la carpeta del proyecto:

```sh
cd web-rifas-anica
```

---

### **2️⃣ Configurar MySQL**  
Debes crear la base de datos **`anica_db`** en MySQL. Para ello:  

1. Abre MySQL desde la terminal o desde **MySQL Workbench**.  
2. Ingresa con el usuario **root** (o el usuario que uses):

   ```sh
   mysql -u root -p
   ```

3. Crea la base de datos:

   ```sql
   CREATE DATABASE anica_db;
   ```

4. (Opcional) Crear un usuario y darle permisos:

   ```sql
   CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin123';
   GRANT ALL PRIVILEGES ON anica_db.* TO 'admin'@'localhost';
   FLUSH PRIVILEGES;
   ```

📌 **IMPORTANTE:**  
Si MySQL da el error **"Access denied"** cuando Django intenta conectar con la base de datos, revisa en el archivo **`settings.py`** que las credenciales sean correctas:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'anica_db',
        'USER': 'admin',
        'PASSWORD': 'admin123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Si cambiaste los valores, actualízalos antes de continuar.

---

### **3️⃣ Crear un entorno virtual**  
Para evitar conflictos con dependencias, usa un entorno virtual:

```sh
python -m venv venv
```

Luego, actívalo:

✅ **En Windows**  
```sh
venv\Scripts\activate
```

✅ **En Mac/Linux**  
```sh
source venv/bin/activate
```

Si tienes problemas con permisos en Windows, ejecuta este comando en **PowerShell** como administrador:

```sh
Set-ExecutionPolicy Unrestricted -Scope Process
```

---

### **4️⃣ Instalar dependencias**  
Con el entorno virtual activado, instala las dependencias del proyecto:

```sh
pip install -r requirements.txt
```

Esto instalará automáticamente Django, MySQL Connector y otras librerías necesarias.

---

### **5️⃣ Aplicar migraciones y cargar datos**  
Para configurar la base de datos correctamente, ejecuta:

```sh
python manage.py migrate
```

Si hay datos iniciales en un archivo JSON (opcional):

```sh
python manage.py loaddata datos_iniciales.json
```

---

### **6️⃣ Crear un superusuario (Opcional, pero recomendado)**  
Para acceder al panel de administración de Django:

```sh
python manage.py createsuperuser
```

Sigue las instrucciones y crea un usuario con nombre, correo y contraseña.

---

### **7️⃣ Ejecutar el servidor**  
¡Todo listo! Ahora puedes correr el servidor de desarrollo:

```sh
python manage.py runserver
```

Si todo está bien, accede en tu navegador a:  
**http://127.0.0.1:8000**

---

## **Comandos útiles**  

| Acción | Comando |
|--------|---------|
| Activar entorno virtual | `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (Mac/Linux) |
| Instalar dependencias | `pip install -r requirements.txt` |
| Aplicar migraciones | `python manage.py migrate` |
| Crear superusuario | `python manage.py createsuperuser` |
| Correr el servidor | `python manage.py runserver` |
| Agregar cambios a Git | `git add .` |
| Guardar cambios en Git | `git commit -m "mensaje"` |
| Subir cambios a GitHub | `git push origin main` |

---

## **Errores comunes y soluciones**  

🔴 **Error:** `django.db.utils.OperationalError: (1044, "Access denied for user 'admin'@'%' to database 'anica_db'")`  
✅ **Solución:** Verifica que el usuario y la contraseña en `settings.py` sean correctos y que MySQL tenga permisos para acceder a la base de datos.

🔴 **Error:** `python: command not found`  
✅ **Solución:** Puede que Python no esté en tu variable de entorno. Usa `py` en lugar de `python` o reinstala Python.

🔴 **Error:** `venv\Scripts\activate : ejecución de scripts está deshabilitada en este sistema`  
✅ **Solución:** Ejecuta en PowerShell (como admin):

```sh
Set-ExecutionPolicy Unrestricted -Scope Process
```

---