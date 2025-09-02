// Tipos principales de la aplicación

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  cedula?: string;
  oficio?: string;
  foto_perfil?: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string;
  reputacion: number;
}

export interface San {
  id: number;
  nombre: string;
  descripcion: string;
  precio_cuota: number;
  precio_total: number;
  numero_cuotas: number;
  frecuencia: string;
  estado: 'activo' | 'finalizado' | 'cancelado';
  fecha_inicio: string;
  fecha_fin: string;
  organizador: User;
  participantes_count: number;
  max_participantes: number;
  created_at: string;
  updated_at: string;
}

export interface Rifa {
  id: number;
  titulo: string;
  descripcion: string;
  precio_ticket: number;
  numero_tickets: number;
  tickets_disponibles: number;
  estado: 'activa' | 'finalizada' | 'cancelada';
  fecha_inicio: string;
  fecha_fin: string;
  organizador: User;
  ganador?: User;
  created_at: string;
  updated_at: string;
}

export interface Ticket {
  id: number;
  rifa: Rifa;
  usuario: User;
  numero: number;
  precio_pagado: number;
  estado: 'pendiente' | 'activo' | 'cancelado';
  fecha_compra: string;
  factura?: Factura;
}

export interface ParticipacionSan {
  id: number;
  san: San;
  usuario: User;
  orden_cobro: number;
  cuotas_pagadas: number;
  fecha_inscripcion: string;
  estado: 'activa' | 'inactiva' | 'finalizada';
}

export interface TurnoSan {
  id: number;
  san: San;
  participante: ParticipacionSan;
  numero_turno: number;
  monto_turno: number;
  estado: 'pendiente' | 'activo' | 'cumplido';
  fecha_activacion?: string;
  fecha_cumplimiento?: string;
}

export interface Cupo {
  id: number;
  participacion: ParticipacionSan;
  numero_semana: number;
  monto_cuota: number;
  fecha_vencimiento: string;
  estado: 'asignado' | 'pagado' | 'vencido';
  fecha_pago?: string;
  factura?: Factura;
}

export interface Factura {
  id: number;
  codigo: string;
  usuario: User;
  monto_total: number;
  monto_pagado: number;
  estado_pago: 'pendiente' | 'confirmado' | 'rechazado' | 'cancelado';
  tipo: 'rifa' | 'san' | 'cuota_san' | 'ticket_rifa' | 'inscripcion_san' | 'otro';
  fecha_emision: string;
  fecha_vencimiento?: string;
  fecha_pago?: string;
  metodo_pago?: string;
  comprobante_pago?: string;
  notas?: string;
}

export interface PagoSimulado {
  id: number;
  codigo_transaccion: string;
  usuario: User;
  factura: Factura;
  metodo_pago: 'paypal' | 'stripe' | 'nequi' | 'efectivo' | 'transferencia';
  monto: number;
  moneda: string;
  estado: 'pendiente' | 'procesando' | 'exitoso' | 'fallido' | 'cancelado';
  referencia_externa?: string;
  fecha_procesamiento?: string;
  tiempo_procesamiento: number;
  intentos: number;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface Comment {
  id: number;
  usuario: User;
  texto: string;
  fecha_creacion: string;
  fecha_actualizacion: string;
  activo: boolean;
  comentario_padre?: Comment;
  respuestas: Comment[];
  votos_positivos: number;
  votos_negativos: number;
  votado_por_usuario?: 'positivo' | 'negativo';
}

export interface Notificacion {
  id: number;
  usuario: User;
  titulo: string;
  mensaje: string;
  tipo: 'pago' | 'turno' | 'comentario' | 'admin' | 'sistema';
  leido: boolean;
  fecha_creacion: string;
  fecha_lectura?: string;
  datos_adicionales?: any;
}

export interface NotificacionMejorada {
  id: number;
  usuario: User;
  titulo: string;
  mensaje: string;
  tipo: 'pago' | 'turno' | 'comentario' | 'admin' | 'sistema';
  canal: 'email' | 'whatsapp' | 'sms' | 'push' | 'interno';
  prioridad: 'baja' | 'media' | 'alta' | 'urgente';
  leido: boolean;
  enviado: boolean;
  fecha_creacion: string;
  fecha_envio?: string;
  fecha_lectura?: string;
  datos_adicionales?: any;
}

export interface SystemLog {
  id: number;
  usuario?: User;
  tipo_accion: string;
  descripcion: string;
  nivel: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  fecha_creacion: string;
  ip_address: string;
  user_agent?: string;
  objeto_relacionado?: any;
  datos_adicionales?: any;
}

export interface SorteoRifa {
  id: number;
  rifa: Rifa;
  ticket_ganador: Ticket;
  fecha_sorteo: string;
  ganador: User;
}

export interface Mensaje {
  id: number;
  remitente: User;
  destinatario: User;
  asunto: string;
  contenido: string;
  leido: boolean;
  fecha_envio: string;
  fecha_lectura?: string;
}

// Tipos para filtros y búsquedas
export interface SanFilters {
  estado?: string;
  precio_min?: number;
  precio_max?: number;
  frecuencia?: string;
  organizador?: number;
}

export interface RifaFilters {
  estado?: string;
  precio_min?: number;
  precio_max?: number;
  organizador?: number;
}

// Tipos para formularios
export interface LoginForm {
  username: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password1: string;
  password2: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  cedula?: string;
  oficio?: string;
}

export interface CommentForm {
  texto: string;
  comentario_padre?: number;
}

export interface PaymentForm {
  metodo_pago: string;
  referencia_externa?: string;
  comprobante?: any;
}

// Tipos para respuestas de API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: any;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// Tipos para navegación
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  Login: undefined;
  Register: undefined;
  Home: undefined;
  SanDetail: { sanId: number };
  RifaDetail: { rifaId: number };
  Payment: { facturaId: number; tipo: string };
  Profile: undefined;
  Notifications: undefined;
  Comments: { contentId: number; contentType: string };
  Admin: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Search: undefined;
  Profile: undefined;
  Notifications: undefined;
  Admin: undefined;
};
