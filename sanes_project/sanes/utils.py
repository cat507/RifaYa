import random
from .models import Ticket, ParticipacionSan
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional, Union


# GANADOR DE RIFA
def elegir_ganador(rifa):
    tickets = list(Ticket.objects.filter(rifa=rifa))
    if not tickets:
        return None
    ganador_ticket = random.choice(tickets)
    rifa.ganador = ganador_ticket.usuario
    rifa.save()
    return ganador_ticket.usuario


# ROTACIÓN DE SAN
def asignar_beneficiario(san):
    beneficiario = ParticipacionSan.objects.filter(san=san, estado_cobro='pending').order_by('orden_cobro').first()
    if beneficiario:
        beneficiario.estado_cobro = 'received'
        beneficiario.save()
        return beneficiario
    return None


def calcular_san_contexto(
    precio_total: Optional[Decimal], 
    total_participantes: Optional[int], 
    frecuencia_pago: Optional[str], 
    fecha_inicio: Optional[date], 
    fecha_fin: Optional[date], 
    numero_cuotas: Optional[int] = None
) -> Dict:
    """
    Calcula métricas de viabilidad para sanes.
    
    Args:
        precio_total: Monto total del san
        total_participantes: Número de participantes
        frecuencia_pago: Frecuencia de pago (diaria, semanal, quincenal, mensual)
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de finalización
        numero_cuotas: Número de cuotas (opcional)
    
    Returns:
        Dict con cálculos y alertas
    """
    if not precio_total or not total_participantes or not frecuencia_pago:
        return {
            'cuota_por_participante_por_periodo': Decimal('0.00'),
            'periodos_necesarios': 0,
            'periodos_disponibles': 0,
            'viable': False,
            'alertas': ['Faltan datos requeridos para el cálculo'],
            'monto_total_aportado': Decimal('0.00'),
            'diferencia': Decimal('0.00')
        }

    # Calcular cuota por participante por periodo
    if numero_cuotas and numero_cuotas > 0:
        # La cuota por participante es el monto total dividido por el número de cuotas
        cuota_por_participante_por_periodo = precio_total / Decimal(numero_cuotas)
        periodos_necesarios = numero_cuotas
    else:
        cuota_por_participante_por_periodo = precio_total
        periodos_necesarios = 1

    # Calcular periodos disponibles según fechas
    periodos_disponibles = 0
    if fecha_inicio and fecha_fin and fecha_fin > fecha_inicio:
        delta_dias = (fecha_fin - fecha_inicio).days
        if frecuencia_pago == 'diaria':
            periodos_disponibles = delta_dias
        elif frecuencia_pago == 'semanal':
            periodos_disponibles = max(1, delta_dias // 7)
        elif frecuencia_pago == 'quincenal':
            periodos_disponibles = max(1, delta_dias // 14)
        elif frecuencia_pago == 'mensual':
            periodos_disponibles = max(1, delta_dias // 30)

    # Calcular monto total que se aportaría con los parámetros actuales
    # Cada participante paga la cuota por periodo, multiplicado por el número de participantes
    monto_total_aportado = cuota_por_participante_por_periodo * Decimal(total_participantes)
    diferencia = monto_total_aportado - precio_total

    # Verificar viabilidad
    viable = True
    alertas = []

    # Verificar si los periodos necesarios caben en el tiempo disponible
    if periodos_disponibles > 0 and numero_cuotas and numero_cuotas > periodos_disponibles:
        viable = False
        alertas.append(f'⚠️ El número de cuotas ({numero_cuotas}) excede los periodos disponibles ({periodos_disponibles}) entre las fechas indicadas.')

    # Verificar si se cubre el monto total
    if monto_total_aportado < precio_total:
        viable = False
        alertas.append(f'⚠️ Los parámetros no cubren el monto total. Faltan ${diferencia:,.2f}')

    # Verificar si las fechas son válidas
    if fecha_inicio and fecha_fin and fecha_fin <= fecha_inicio:
        viable = False
        alertas.append('⚠️ La fecha de fin debe ser posterior a la fecha de inicio.')

    # Verificar si el número de participantes es razonable
    if total_participantes < 2:
        viable = False
        alertas.append('⚠️ Se requieren al menos 2 participantes para un san.')

    # Agregar información adicional si es viable
    if viable:
        alertas.append(f'✅ San viable: Cada participante pagará ${cuota_por_participante_por_periodo:,.2f} por periodo')
        if periodos_disponibles > 0:
            alertas.append(f'✅ Tiempo disponible: {periodos_disponibles} periodos entre las fechas')

    # Calcular fechas sugeridas si no se proporcionan
    fechas_sugeridas = {}
    if precio_total and total_participantes and numero_cuotas and frecuencia_pago:
        fechas_sugeridas = calcular_fechas_sugeridas_san(
            precio_total, total_participantes, numero_cuotas, frecuencia_pago
        )
    
    return {
        'cuota_por_participante_por_periodo': cuota_por_participante_por_periodo.quantize(Decimal('0.01')),
        'periodos_necesarios': periodos_necesarios,
        'periodos_disponibles': periodos_disponibles,
        'viable': viable,
        'alertas': alertas,
        'monto_total_aportado': monto_total_aportado.quantize(Decimal('0.01')),
        'diferencia': diferencia.quantize(Decimal('0.01')),
        'precio_total': precio_total,
        'total_participantes': total_participantes,
        'frecuencia_pago': frecuencia_pago,
        'fechas_sugeridas': fechas_sugeridas
    }


def calcular_rifa_contexto(
    precio_ticket: Optional[Decimal], 
    total_tickets: Optional[int], 
    valor_premio_monetario: Optional[Decimal] = None
) -> Dict:
    """
    Calcula métricas de viabilidad para rifas.
    
    Args:
        precio_ticket: Precio por ticket
        total_tickets: Total de tickets disponibles
        valor_premio_monetario: Valor monetario del premio (opcional)
    
    Returns:
        Dict con cálculos y alertas
    """
    if not precio_ticket or not total_tickets:
        return {
            'recaudacion_minima_esperada': Decimal('0.00'),
            'minimo_participantes_para_cubrir_premio': None,
            'viable': False,
            'alertas': ['Faltan datos requeridos para el cálculo'],
            'ganancia_esperada': Decimal('0.00'),
            'porcentaje_ganancia': Decimal('0.00')
        }

    # Calcular recaudación mínima esperada
    recaudacion_minima_esperada = precio_ticket * Decimal(total_tickets)
    
    # Calcular ganancia esperada si hay valor de premio
    ganancia_esperada = Decimal('0.00')
    porcentaje_ganancia = Decimal('0.00')
    minimo_participantes_para_cubrir_premio = None
    
    viable = True
    alertas = []

    if valor_premio_monetario is not None and valor_premio_monetario > 0:
        ganancia_esperada = recaudacion_minima_esperada - valor_premio_monetario
        if recaudacion_minima_esperada > 0:
            porcentaje_ganancia = (ganancia_esperada / recaudacion_minima_esperada) * 100
        
        # Calcular mínimo de participantes para cubrir el premio
        if precio_ticket > 0:
            minimo_participantes_para_cubrir_premio = (valor_premio_monetario / precio_ticket).quantize(Decimal('0.01'))
        
        # Verificar viabilidad
        if recaudacion_minima_esperada < valor_premio_monetario:
            viable = False
            alertas.append(f'⚠️ Con los parámetros actuales, no se cubre el valor del premio. Faltan ${valor_premio_monetario - recaudacion_minima_esperada:,.2f}')
        elif ganancia_esperada < 0:
            viable = False
            alertas.append(f'⚠️ La rifa generaría pérdidas de ${abs(ganancia_esperada):,.2f}')
        else:
            alertas.append(f'✅ Rifa viable: Ganancia esperada ${ganancia_esperada:,.2f} ({porcentaje_ganancia:.1f}%)')
            alertas.append(f'✅ Mínimo de participantes para cubrir premio: {minimo_participantes_para_cubrir_premio}')
    else:
        alertas.append(f'✅ Rifa sin premio monetario: Recaudación esperada ${recaudacion_minima_esperada:,.2f}')

    # Verificar parámetros básicos
    if precio_ticket <= 0:
        viable = False
        alertas.append('⚠️ El precio del ticket debe ser mayor a 0.')

    if total_tickets <= 0:
        viable = False
        alertas.append('⚠️ El número de tickets debe ser mayor a 0.')

    if total_tickets > 10000:
        alertas.append('⚠️ Considera si realmente necesitas más de 10,000 tickets.')

    # Calcular parámetros sugeridos si no se proporcionan todos los datos
    parametros_sugeridos = {}
    if valor_premio_monetario and (not precio_ticket or not total_tickets):
        parametros_sugeridos = calcular_parametros_sugeridos_rifa(
            valor_premio=valor_premio_monetario,
            precio_ticket_deseado=precio_ticket,
            total_tickets_deseado=total_tickets
        )
    
    return {
        'recaudacion_minima_esperada': recaudacion_minima_esperada.quantize(Decimal('0.01')),
        'minimo_participantes_para_cubrir_premio': minimo_participantes_para_cubrir_premio,
        'viable': viable,
        'alertas': alertas,
        'ganancia_esperada': ganancia_esperada.quantize(Decimal('0.01')),
        'porcentaje_ganancia': porcentaje_ganancia.quantize(Decimal('0.1')),
        'precio_ticket': precio_ticket,
        'total_tickets': total_tickets,
        'valor_premio_monetario': valor_premio_monetario,
        'parametros_sugeridos': parametros_sugeridos
    }


def formatear_moneda(valor: Decimal) -> str:
    """Formatea un valor decimal como moneda."""
    return f"${valor:,.2f}"


def formatear_porcentaje(valor: Decimal) -> str:
    """Formatea un valor decimal como porcentaje."""
    return f"{valor:.1f}%"


def calcular_fechas_sugeridas_san(
    precio_total: Decimal,
    total_participantes: int,
    numero_cuotas: int,
    frecuencia_pago: str
) -> Dict:
    """
    Calcula fechas sugeridas para un san basado en los parámetros.
    
    Args:
        precio_total: Monto total del san
        total_participantes: Número de participantes
        numero_cuotas: Número de cuotas
        frecuencia_pago: Frecuencia de pago
    
    Returns:
        Dict con fechas sugeridas
    """
    from datetime import date, timedelta
    
    # Fecha de inicio sugerida (hoy)
    fecha_inicio_sugerida = date.today()
    
    # Calcular días necesarios según frecuencia y número de cuotas
    dias_por_periodo = {
        'diaria': 1,
        'semanal': 7,
        'quincenal': 14,
        'mensual': 30
    }
    
    dias_por_periodo_valor = dias_por_periodo.get(frecuencia_pago, 30)
    dias_totales_necesarios = (numero_cuotas - 1) * dias_por_periodo_valor
    
    # Fecha de fin sugerida
    fecha_fin_sugerida = fecha_inicio_sugerida + timedelta(days=dias_totales_necesarios)
    
    # Calcular cuota por participante
    cuota_por_participante = precio_total / Decimal(numero_cuotas)
    
    return {
        'fecha_inicio_sugerida': fecha_inicio_sugerida,
        'fecha_fin_sugerida': fecha_fin_sugerida,
        'dias_totales': dias_totales_necesarios,
        'cuota_por_participante': cuota_por_participante.quantize(Decimal('0.01')),
        'periodos_por_mes': 30 // dias_por_periodo_valor if dias_por_periodo_valor > 0 else 1
    }


def calcular_parametros_sugeridos_rifa(
    valor_premio: Optional[Decimal] = None,
    precio_ticket_deseado: Optional[Decimal] = None,
    total_tickets_deseado: Optional[int] = None
) -> Dict:
    """
    Calcula parámetros sugeridos para una rifa.
    
    Args:
        valor_premio: Valor del premio (opcional)
        precio_ticket_deseado: Precio de ticket deseado (opcional)
        total_tickets_deseado: Total de tickets deseado (opcional)
    
    Returns:
        Dict con parámetros sugeridos
    """
    sugerencias = {}
    
    if valor_premio:
        # Si se proporciona el valor del premio, sugerir precio y cantidad de tickets
        if not precio_ticket_deseado:
            # Sugerir precio de ticket basado en el valor del premio
            if valor_premio <= 100:
                precio_sugerido = Decimal('5.00')
            elif valor_premio <= 500:
                precio_sugerido = Decimal('10.00')
            elif valor_premio <= 1000:
                precio_sugerido = Decimal('20.00')
            else:
                precio_sugerido = Decimal('50.00')
            
            sugerencias['precio_ticket_sugerido'] = precio_sugerido
        
        if not total_tickets_deseado:
            # Sugerir cantidad de tickets para cubrir el premio con ganancia
            precio_efectivo = precio_ticket_deseado or sugerencias.get('precio_ticket_sugerido', Decimal('10.00'))
            tickets_minimos = (valor_premio / precio_efectivo).quantize(Decimal('0.01'))
            # Agregar 20% de ganancia
            tickets_sugeridos = int(tickets_minimos * Decimal('1.2'))
            sugerencias['total_tickets_sugerido'] = max(50, tickets_sugeridos)
    
    # Calcular recaudación esperada con parámetros sugeridos
    if 'precio_ticket_sugerido' in sugerencias and 'total_tickets_sugerido' in sugerencias:
        recaudacion = sugerencias['precio_ticket_sugerido'] * Decimal(sugerencias['total_tickets_sugerido'])
        if valor_premio:
            ganancia = recaudacion - valor_premio
            porcentaje_ganancia = (ganancia / recaudacion * 100) if recaudacion > 0 else 0
            sugerencias['ganancia_esperada'] = ganancia.quantize(Decimal('0.01'))
            sugerencias['porcentaje_ganancia'] = porcentaje_ganancia.quantize(Decimal('0.1'))
    
    return sugerencias