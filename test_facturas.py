#!/usr/bin/env python
"""
Script para probar el sistema de facturas de Rifas Anica
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanes_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from sanes.models import Rifa, San, Factura, ComprobantePago
from django.utils import timezone

User = get_user_model()

def crear_facturas_prueba():
    """Crear facturas de prueba para diferentes escenarios"""
    
    print("🧪 Creando facturas de prueba...")
    
    # Obtener usuarios de prueba
    try:
        usuario1 = User.objects.get(username='usuario1')
        usuario2 = User.objects.get(username='usuario2')
    except User.DoesNotExist:
        print("❌ Usuarios de prueba no encontrados. Creando usuarios...")
        usuario1 = User.objects.create_user(
            username='usuario1',
            email='usuario1@test.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Uno'
        )
        usuario2 = User.objects.create_user(
            username='usuario2',
            email='usuario2@test.com',
            password='testpass123',
            first_name='Usuario',
            last_name='Dos'
        )
    
    # Obtener rifas y sanes de prueba
    try:
        rifa1 = Rifa.objects.first()
        san1 = San.objects.first()
    except:
        print("❌ No hay rifas o sanes disponibles. Creando algunos...")
        rifa1 = Rifa.objects.create(
            titulo='Rifa de Prueba 1',
            descripcion='Rifa para probar el sistema de facturas',
            precio_ticket=Decimal('10.00'),
            fecha_inicio=timezone.now(),
            fecha_fin=timezone.now() + timedelta(days=30),
            estado='activa',
            creador=usuario1
        )
        san1 = San.objects.create(
            nombre='San de Prueba 1',
            descripcion='San para probar el sistema de facturas',
            precio=Decimal('50.00'),
            fecha_inicio=timezone.now(),
            fecha_fin=timezone.now() + timedelta(days=60),
            estado='activo',
            creador=usuario1
        )
    
    # Crear facturas de diferentes tipos y estados
    facturas_creadas = []
    
    # Factura de rifa pagada
    factura1 = Factura.objects.create(
        usuario=usuario1,
        concepto='Compra de tickets - Rifa de Prueba 1',
        monto=Decimal('50.00'),
        tipo='rifa',
        estado='pagada',
        fecha_emision=timezone.now() - timedelta(days=5),
        fecha_pago=timezone.now() - timedelta(days=3),
        rifa=rifa1
    )
    facturas_creadas.append(factura1)
    print(f"✅ Factura creada: {factura1.id_unico} - Rifa pagada")
    
    # Factura de san pendiente
    factura2 = Factura.objects.create(
        usuario=usuario1,
        concepto='Inscripción - San de Prueba 1',
        monto=Decimal('50.00'),
        tipo='san',
        estado='pendiente',
        fecha_emision=timezone.now() - timedelta(days=2),
        fecha_vencimiento=timezone.now() + timedelta(days=5),
        san=san1
    )
    facturas_creadas.append(factura2)
    print(f"✅ Factura creada: {factura2.id_unico} - San pendiente")
    
    # Factura vencida
    factura3 = Factura.objects.create(
        usuario=usuario2,
        concepto='Compra de tickets - Rifa de Prueba 1',
        monto=Decimal('30.00'),
        tipo='rifa',
        estado='vencida',
        fecha_emision=timezone.now() - timedelta(days=10),
        fecha_vencimiento=timezone.now() - timedelta(days=2),
        rifa=rifa1
    )
    facturas_creadas.append(factura3)
    print(f"✅ Factura creada: {factura3.id_unico} - Rifa vencida")
    
    # Factura cancelada
    factura4 = Factura.objects.create(
        usuario=usuario2,
        concepto='Inscripción - San de Prueba 1',
        monto=Decimal('50.00'),
        tipo='san',
        estado='cancelada',
        fecha_emision=timezone.now() - timedelta(days=15),
        san=san1
    )
    facturas_creadas.append(factura4)
    print(f"✅ Factura creada: {factura4.id_unico} - San cancelada")
    
    # Factura de otro tipo
    factura5 = Factura.objects.create(
        usuario=usuario1,
        concepto='Servicio adicional',
        monto=Decimal('25.00'),
        tipo='otro',
        estado='pendiente',
        fecha_emision=timezone.now(),
        fecha_vencimiento=timezone.now() + timedelta(days=7)
    )
    facturas_creadas.append(factura5)
    print(f"✅ Factura creada: {factura5.id_unico} - Otro tipo pendiente")
    
    # Crear comprobantes de pago para algunas facturas
    print("\n📄 Creando comprobantes de pago...")
    
    # Comprobante aprobado para factura pagada
    comprobante1 = ComprobantePago.objects.create(
        factura=factura1,
        archivo='comprobantes/test_comprobante1.pdf',
        metodo_pago='transferencia',
        fecha_pago=timezone.now() - timedelta(days=3),
        monto_pagado=Decimal('50.00'),
        numero_referencia='TRX123456789',
        estado='aprobado',
        notas='Pago realizado por transferencia bancaria'
    )
    print(f"✅ Comprobante creado: #{comprobante1.id} - Aprobado")
    
    # Comprobante pendiente para factura pendiente
    comprobante2 = ComprobantePago.objects.create(
        factura=factura2,
        archivo='comprobantes/test_comprobante2.pdf',
        metodo_pago='deposito',
        fecha_pago=timezone.now() - timedelta(days=1),
        monto_pagado=Decimal('50.00'),
        numero_referencia='DEP987654321',
        estado='pendiente',
        notas='Depósito bancario realizado'
    )
    print(f"✅ Comprobante creado: #{comprobante2.id} - Pendiente")
    
    # Comprobante rechazado para factura vencida
    comprobante3 = ComprobantePago.objects.create(
        factura=factura3,
        archivo='comprobantes/test_comprobante3.pdf',
        metodo_pago='efectivo',
        fecha_pago=timezone.now() - timedelta(days=1),
        monto_pagado=Decimal('25.00'),
        estado='rechazado',
        notas='Monto insuficiente'
    )
    print(f"✅ Comprobante creado: #{comprobante3.id} - Rechazado")
    
    print(f"\n🎉 Se crearon {len(facturas_creadas)} facturas de prueba")
    print(f"📄 Se crearon 3 comprobantes de pago")
    
    return facturas_creadas

def mostrar_estadisticas():
    """Mostrar estadísticas del sistema de facturas"""
    
    print("\n📊 ESTADÍSTICAS DEL SISTEMA DE FACTURAS")
    print("=" * 50)
    
    total_facturas = Factura.objects.count()
    facturas_pagadas = Factura.objects.filter(estado='pagada').count()
    facturas_pendientes = Factura.objects.filter(estado='pendiente').count()
    facturas_vencidas = Factura.objects.filter(estado='vencida').count()
    facturas_canceladas = Factura.objects.filter(estado='cancelada').count()
    
    total_comprobantes = ComprobantePago.objects.count()
    comprobantes_aprobados = ComprobantePago.objects.filter(estado='aprobado').count()
    comprobantes_pendientes = ComprobantePago.objects.filter(estado='pendiente').count()
    comprobantes_rechazados = ComprobantePago.objects.filter(estado='rechazado').count()
    
    print(f"📋 Total de facturas: {total_facturas}")
    print(f"✅ Facturas pagadas: {facturas_pagadas}")
    print(f"⏳ Facturas pendientes: {facturas_pendientes}")
    print(f"⚠️  Facturas vencidas: {facturas_vencidas}")
    print(f"❌ Facturas canceladas: {facturas_canceladas}")
    
    print(f"\n📄 Total de comprobantes: {total_comprobantes}")
    print(f"✅ Comprobantes aprobados: {comprobantes_aprobados}")
    print(f"⏳ Comprobantes pendientes: {comprobantes_pendientes}")
    print(f"❌ Comprobantes rechazados: {comprobantes_rechazados}")
    
    # Estadísticas por tipo
    print(f"\n📈 POR TIPO:")
    for tipo, nombre in Factura.TIPOS_CHOICES:
        count = Factura.objects.filter(tipo=tipo).count()
        print(f"   {nombre}: {count}")
    
    # Estadísticas por usuario
    print(f"\n👥 POR USUARIO:")
    for user in User.objects.all():
        count = Factura.objects.filter(usuario=user).count()
        print(f"   {user.get_full_name_or_username()}: {count} facturas")

def limpiar_datos_prueba():
    """Limpiar datos de prueba"""
    
    print("\n🧹 Limpiando datos de prueba...")
    
    # Eliminar comprobantes de prueba
    comprobantes_eliminados = ComprobantePago.objects.filter(
        numero_referencia__in=['TRX123456789', 'DEP987654321']
    ).delete()
    
    # Eliminar facturas de prueba
    facturas_eliminadas = Factura.objects.filter(
        concepto__contains='Prueba'
    ).delete()
    
    print(f"✅ Se eliminaron {comprobantes_eliminados[0]} comprobantes")
    print(f"✅ Se eliminaron {facturas_eliminadas[0]} facturas")

def main():
    """Función principal"""
    
    print("🚀 SISTEMA DE FACTURAS - RIFAS ANICA")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'crear':
            crear_facturas_prueba()
        elif comando == 'estadisticas':
            mostrar_estadisticas()
        elif comando == 'limpiar':
            limpiar_datos_prueba()
        elif comando == 'completo':
            crear_facturas_prueba()
            mostrar_estadisticas()
        else:
            print("❌ Comando no válido. Usa: crear, estadisticas, limpiar, o completo")
    else:
        print("📝 Uso: python test_facturas.py [comando]")
        print("   crear - Crear facturas de prueba")
        print("   estadisticas - Mostrar estadísticas")
        print("   limpiar - Limpiar datos de prueba")
        print("   completo - Crear datos y mostrar estadísticas")

if __name__ == '__main__':
    main()

