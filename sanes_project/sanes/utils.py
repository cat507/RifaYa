import random
from .models import TicketRifa, ParticipanteSan

# GANADOR DE RIFA
def elegir_ganador(rifa):
    tickets = list(TicketRifa.objects.filter(rifa=rifa))
    if not tickets:
        return None
    ganador_ticket = random.choice(tickets)
    rifa.ganador = ganador_ticket.usuario
    rifa.save()
    return ganador_ticket.usuario


# ROTACIÓN DE SAN
def asignar_beneficiario(san):
    beneficiario = ParticipanteSan.objects.filter(san=san, estado_cobro='pending').order_by('orden_cobro').first()
    if beneficiario:
        beneficiario.estado_cobro = 'received'
        beneficiario.save()
        return beneficiario
    return None