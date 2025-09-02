import axios, { AxiosInstance, AxiosResponse } from 'react-native-axios';
import AsyncStorage from 'react-native-async-storage';
import {
  User,
  San,
  Rifa,
  Ticket,
  ParticipacionSan,
  TurnoSan,
  Cupo,
  Factura,
  PagoSimulado,
  Comment,
  Notificacion,
  NotificacionMejorada,
  SystemLog,
  SorteoRifa,
  Mensaje,
  LoginForm,
  RegisterForm,
  CommentForm,
  PaymentForm,
  SanFilters,
  RifaFilters,
  ApiResponse,
  PaginatedResponse,
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    // Cambiar según tu configuración
    this.baseURL = 'http://192.168.1.106:8000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token de autenticación
    this.api.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Interceptor para manejar errores
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expirado, redirigir al login
          await AsyncStorage.removeItem('authToken');
          await AsyncStorage.removeItem('userData');
        }
        return Promise.reject(error);
      }
    );
  }

  // ===== AUTENTICACIÓN =====
  async login(credentials: LoginForm): Promise<ApiResponse<{ token: string; user: User }>> {
    try {
      const response = await this.api.post('/api/auth/login/', credentials);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.message || 'Error en el login',
        errors: error.response?.data?.errors,
      };
    }
  }

  async register(userData: RegisterForm): Promise<ApiResponse<{ token: string; user: User }>> {
    try {
      const response = await this.api.post('/api/auth/register/', userData);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.message || 'Error en el registro',
        errors: error.response?.data?.errors,
      };
    }
  }

  async logout(): Promise<ApiResponse<null>> {
    try {
      await this.api.post('/api/auth/logout/');
      await AsyncStorage.removeItem('authToken');
      await AsyncStorage.removeItem('userData');
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error en el logout',
      };
    }
  }

  // ===== SANES =====
  async getSanes(filters?: SanFilters): Promise<ApiResponse<PaginatedResponse<San>>> {
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await this.api.get(`/api/sanes/?${params.toString()}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener SANes',
      };
    }
  }

  async getSanDetail(sanId: number): Promise<ApiResponse<San>> {
    try {
      const response = await this.api.get(`/api/sanes/${sanId}/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener detalle del SAN',
      };
    }
  }

  async joinSan(sanId: number): Promise<ApiResponse<ParticipacionSan>> {
    try {
      const response = await this.api.post(`/api/sanes/${sanId}/join/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al unirse al SAN',
      };
    }
  }

  async getSanTurns(sanId: number): Promise<ApiResponse<TurnoSan[]>> {
    try {
      const response = await this.api.get(`/api/sanes/${sanId}/turns/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener turnos del SAN',
      };
    }
  }

  async getSanPayments(sanId: number): Promise<ApiResponse<PagoSimulado[]>> {
    try {
      const response = await this.api.get(`/api/sanes/${sanId}/payments/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener pagos del SAN',
      };
    }
  }

  // ===== RIFAS =====
  async getRifas(filters?: RifaFilters): Promise<ApiResponse<PaginatedResponse<Rifa>>> {
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await this.api.get(`/api/rifas/?${params.toString()}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener rifas',
      };
    }
  }

  async getRifaDetail(rifaId: number): Promise<ApiResponse<Rifa>> {
    try {
      const response = await this.api.get(`/api/rifas/${rifaId}/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener detalle de la rifa',
      };
    }
  }

  async buyTicket(rifaId: number, ticketData: { numero: number }): Promise<ApiResponse<Ticket>> {
    try {
      const response = await this.api.post(`/api/rifas/${rifaId}/buy-ticket/`, ticketData);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al comprar ticket',
      };
    }
  }

  async getUserTickets(): Promise<ApiResponse<Ticket[]>> {
    try {
      const response = await this.api.get('/api/user/tickets/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener tickets del usuario',
      };
    }
  }

  // ===== PAGOS =====
  async createPayment(facturaId: number, paymentData: PaymentForm): Promise<ApiResponse<PagoSimulado>> {
    try {
      const response = await this.api.post(`/api/payments/create/`, {
        factura_id: facturaId,
        ...paymentData,
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al crear pago',
      };
    }
  }

  async uploadPaymentProof(paymentId: number, proof: any): Promise<ApiResponse<PagoSimulado>> {
    try {
      const formData = new FormData();
      formData.append('comprobante', proof);

      const response = await this.api.patch(`/api/payments/${paymentId}/upload-proof/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al subir comprobante',
      };
    }
  }

  async getPaymentStatus(paymentId: number): Promise<ApiResponse<PagoSimulado>> {
    try {
      const response = await this.api.get(`/api/payments/${paymentId}/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener estado del pago',
      };
    }
  }

  // ===== COMENTARIOS =====
  async getComments(contentType: string, contentId: number): Promise<ApiResponse<Comment[]>> {
    try {
      const response = await this.api.get(`/api/comments/${contentType}/${contentId}/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener comentarios',
      };
    }
  }

  async addComment(contentType: string, contentId: number, commentData: CommentForm): Promise<ApiResponse<Comment>> {
    try {
      const response = await this.api.post(`/api/comments/${contentType}/${contentId}/`, commentData);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al agregar comentario',
      };
    }
  }

  async deleteComment(commentId: number): Promise<ApiResponse<null>> {
    try {
      await this.api.delete(`/api/comments/${commentId}/`);
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al eliminar comentario',
      };
    }
  }

  // ===== NOTIFICACIONES =====
  async getNotifications(): Promise<ApiResponse<NotificacionMejorada[]>> {
    try {
      const response = await this.api.get('/api/notifications/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener notificaciones',
      };
    }
  }

  async markNotificationAsRead(notificationId: number): Promise<ApiResponse<NotificacionMejorada>> {
    try {
      const response = await this.api.patch(`/api/notifications/${notificationId}/mark-read/`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al marcar notificación como leída',
      };
    }
  }

  async markAllNotificationsAsRead(): Promise<ApiResponse<null>> {
    try {
      await this.api.post('/api/notifications/mark-all-read/');
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al marcar todas las notificaciones como leídas',
      };
    }
  }

  // ===== USUARIO =====
  async getUserProfile(): Promise<ApiResponse<User>> {
    try {
      const response = await this.api.get('/api/user/profile/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener perfil del usuario',
      };
    }
  }

  async updateUserProfile(userData: Partial<User>): Promise<ApiResponse<User>> {
    try {
      const response = await this.api.patch('/api/user/profile/', userData);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al actualizar perfil',
      };
    }
  }

  async getUserParticipations(): Promise<ApiResponse<ParticipacionSan[]>> {
    try {
      const response = await this.api.get('/api/user/participations/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener participaciones del usuario',
      };
    }
  }

  async getUserFacturas(): Promise<ApiResponse<Factura[]>> {
    try {
      const response = await this.api.get('/api/user/facturas/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener facturas del usuario',
      };
    }
  }

  // ===== ADMIN =====
  async getAdminDashboard(): Promise<ApiResponse<any>> {
    try {
      const response = await this.api.get('/api/admin/dashboard/');
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener dashboard de administración',
      };
    }
  }

  async sendNotificationToUser(userId: number, notificationData: {
    titulo: string;
    mensaje: string;
    tipo: string;
    canal: string;
    prioridad: string;
  }): Promise<ApiResponse<NotificacionMejorada>> {
    try {
      const response = await this.api.post(`/api/admin/users/${userId}/send-notification/`, notificationData);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al enviar notificación',
      };
    }
  }

  async getSystemLogs(filters?: any): Promise<ApiResponse<PaginatedResponse<SystemLog>>> {
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined) {
            params.append(key, value.toString());
          }
        });
      }

      const response = await this.api.get(`/api/admin/logs/?${params.toString()}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al obtener logs del sistema',
      };
    }
  }

  // ===== UTILIDADES =====
  async uploadImage(image: any, type: 'profile' | 'payment_proof' | 'other'): Promise<ApiResponse<{ url: string }>> {
    try {
      const formData = new FormData();
      formData.append('image', image);
      formData.append('type', type);

      const response = await this.api.post('/api/upload-image/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return {
        success: false,
        message: 'Error al subir imagen',
      };
    }
  }

  // ===== SIMULACIÓN (para cuando el backend no esté listo) =====
  async simulatePayment(facturaId: number, paymentData: PaymentForm): Promise<ApiResponse<PagoSimulado>> {
    // Simulación de pago para desarrollo
    const simulatedPayment: PagoSimulado = {
      id: Math.floor(Math.random() * 10000),
      codigo_transaccion: `SIM-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
      usuario: {} as User, // Se llenará con datos del usuario actual
      factura: {} as Factura, // Se llenará con datos de la factura
      metodo_pago: paymentData.metodo_pago as any,
      monto: 0, // Se llenará con el monto de la factura
      moneda: 'USD',
      estado: 'pendiente',
      referencia_externa: paymentData.referencia_externa,
      fecha_procesamiento: undefined,
      tiempo_procesamiento: 0,
      intentos: 1,
      fecha_creacion: new Date().toISOString(),
      fecha_actualizacion: new Date().toISOString(),
    };

    return {
      success: true,
      data: simulatedPayment,
      message: 'Pago simulado creado exitosamente',
    };
  }

  async simulateNotification(userId: number, notificationData: any): Promise<ApiResponse<NotificacionMejorada>> {
    // Simulación de notificación para desarrollo
    const simulatedNotification: NotificacionMejorada = {
      id: Math.floor(Math.random() * 10000),
      usuario: {} as User,
      titulo: notificationData.titulo,
      mensaje: notificationData.mensaje,
      tipo: notificationData.tipo as any,
      canal: notificationData.canal as any,
      prioridad: notificationData.prioridad as any,
      leido: false,
      enviado: true,
      fecha_creacion: new Date().toISOString(),
      fecha_envio: new Date().toISOString(),
      fecha_lectura: undefined,
      datos_adicionales: notificationData.datos_adicionales,
    };

    return {
      success: true,
      data: simulatedNotification,
      message: 'Notificación simulada enviada exitosamente',
    };
  }
}

export default new ApiService();
