import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, "sanes")  # Ajusta si tu app no se llama sanes

# Mapeo de templates correctos
TEMPLATE_MAP = {
    "registration/login.html": "account/login.html",
    "registration/register.html": "account/register.html",
    "home.html": "misc/home.html",
    "rifa_list.html": "raffle/rifa_list.html",
    "rifa_detail.html": "raffle/raffle_detail.html",
    "rifa_create.html": "raffle/rifa_create.html",
    "rifa_update.html": "raffle/create_raffle.html",
    "rifa_checkout.html": "raffle/raffle_checkout.html",
    "san_list.html": "san/san_list.html",
    "san_detail.html": "san/san_detail.html",
    "san_create.html": "san/create_san.html",
    "san_update.html": "san/mis_sanes.html",
    "san_checkout.html": "san/cuotas_san.html",
    "factura_list.html": "orders/factura_list.html",
    "factura_detail.html": "orders/factura_detail.html",
    "user_profile.html": "user/profile.html",
    "admin_dashboard.html": "admin/dashboard.html",
    "reporte_rifas.html": "reports/reporte_rifas.html",
    "reporte_sanes.html": "reports/reporte_sanes.html",
    "errors/404.html": "misc/errors/404.html",
    "errors/500.html": "misc/errors/500.html",
}

def replace_templates_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    updated = content

    # Buscar template_name = '...'
    for old, new in TEMPLATE_MAP.items():
        updated = re.sub(
            rf"(template_name\s*=\s*['\"]){old}(['\"])",
            rf"\1{new}\2",
            updated
        )
        # Buscar render(request, '...')
        updated = re.sub(
            rf"(render\(.*?,\s*['\"]){old}(['\"])",
            rf"\1{new}\2",
            updated
        )

    if updated != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"✅ Actualizado: {file_path}")

def update_views():
    for root, _, files in os.walk(APP_DIR):
        for file in files:
            if file.endswith(".py") and file == "views.py":
                replace_templates_in_file(os.path.join(root, file))

if __name__ == "__main__":
    update_views()
