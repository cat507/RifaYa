import os
import shutil

# Ruta a la carpeta templates actual
TEMPLATES_DIR = r"C:\Users\Daniel\Documents\programacion\web para rifas anica\sanes_project\sanes\templates"

# Mapeo de templates -> carpeta destino
TEMPLATE_MAP = {
    # Raffles
    "raffle_detail.html": "raffle",
    "raffle_checkout.html": "raffle",
    "rafflecompleted.html": "raffle",
    "create_raffle.html": "raffle",
    "rifa_create.html": "raffle",
    "rifa_list.html": "raffle",

    # Sanes
    "san_list.html": "san",
    "san_detail.html": "san",
    "create_san.html": "san",
    "cuotas_san.html": "san",
    "mis_sanes.html": "san",
    "my_contributions_view.html": "san",

    # Usuarios
    "user_profile_view.html": "user",
    "edit_userprofile": "user",   # ⚠️ parece que no tiene extensión .html
    "cambiar_foto_perfil.html": "user",

    # Órdenes
    "confirm_purchase.html": "orders",
    "confirmar_compra.html": "orders",
    "ordersummary.html": "orders",
    "order_confirmation.html": "orders",
    "admin_order_report.html": "orders",

    # Autenticación
    "login.html": "account",
    "register.html": "account",

    # Otros
    "home.html": "misc",
    "globals.css": "static/css",
    "style.css": "static/css",

    # Base y comunes
    "base.html": ".",            # raíz de templates
    "footer.html": "includes",
    "navbar.html": "includes",
}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_if_missing(path):
    """Crea un archivo vacío si no existe"""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("")  # vacío

def organize_templates():
    for filename, folder in TEMPLATE_MAP.items():
        src = os.path.join(TEMPLATES_DIR, filename)
        dest_dir = os.path.join(TEMPLATES_DIR, folder)
        ensure_dir(dest_dir)
        dest = os.path.join(dest_dir, filename)

        if os.path.exists(src):  # mover si existe
            print(f"Moviendo {filename} -> {dest_dir}")
            shutil.move(src, dest)
        else:  # crear vacío si no existe
            print(f"⚠️ {filename} no existe, creando vacío en {dest_dir}")
            create_if_missing(dest)

if __name__ == "__main__":
    organize_templates()
    print("✅ Organización terminada. Ahora ejecuta el Script 2 para actualizar referencias.")
