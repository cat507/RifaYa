import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Dimensions,
  RefreshControl,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { San, ParticipacionSan, TurnoSan, PagoSimulado, Comment } from '../types';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

type SanDetailScreenNavigationProp = StackNavigationProp<RootStackParamList, 'SanDetail'>;
type SanDetailScreenRouteProp = RouteProp<RootStackParamList, 'SanDetail'>;

const { width } = Dimensions.get('window');

const SanDetailScreen: React.FC = () => {
  const navigation = useNavigation<SanDetailScreenNavigationProp>();
  const route = useRoute<SanDetailScreenRouteProp>();
  const { user } = useAuth();
  
  const { sanId } = route.params;
  
  const [san, setSan] = useState<San | null>(null);
  const [participacion, setParticipacion] = useState<ParticipacionSan | null>(null);
  const [turnos, setTurnos] = useState<TurnoSan[]>([]);
  const [pagos, setPagos] = useState<PagoSimulado[]>([]);
  const [comentarios, setComentarios] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'info' | 'turnos' | 'pagos' | 'comentarios'>('info');
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    loadSanData();
  }, [sanId]);

  const loadSanData = async () => {
    try {
      setLoading(true);
      
      // Cargar detalles del SAN
      const sanResponse = await apiService.getSanDetail(sanId);
      if (sanResponse.success && sanResponse.data) {
        setSan(sanResponse.data);
      }

      // Cargar turnos del SAN
      const turnosResponse = await apiService.getSanTurns(sanId);
      if (turnosResponse.success && turnosResponse.data) {
        setTurnos(turnosResponse.data);
      }

      // Cargar pagos del SAN
      const pagosResponse = await apiService.getSanPayments(sanId);
      if (pagosResponse.success && pagosResponse.data) {
        setPagos(pagosResponse.data);
      }

      // Cargar comentarios del SAN
      const comentariosResponse = await apiService.getComments('san', sanId);
      if (comentariosResponse.success && comentariosResponse.data) {
        setComentarios(comentariosResponse.data);
      }

      // Verificar si el usuario ya participa
      if (user) {
        const participacionesResponse = await apiService.getUserParticipations();
        if (participacionesResponse.success && participacionesResponse.data) {
          const userParticipacion = participacionesResponse.data.find(
            p => p.san.id === sanId
          );
          if (userParticipacion) {
            setParticipacion(userParticipacion);
          }
        }
      }
    } catch (error) {
      console.error('Error loading SAN data:', error);
      Alert.alert('Error', 'No se pudieron cargar los datos del SAN');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadSanData();
    setRefreshing(false);
  };

  const handleJoinSan = async () => {
    if (!user) {
      Alert.alert('Error', 'Debes iniciar sesión para unirte al SAN');
      return;
    }

    try {
      setJoining(true);
      const response = await apiService.joinSan(sanId);
      
      if (response.success && response.data) {
        setParticipacion(response.data);
        Alert.alert(
          '¡Éxito!',
          'Te has unido exitosamente al SAN. Se te asignará un turno automáticamente.',
          [{ text: 'OK' }]
        );
        
        // Recargar datos
        await loadSanData();
      } else {
        Alert.alert('Error', response.message || 'No se pudo unir al SAN');
      }
    } catch (error) {
      console.error('Error joining SAN:', error);
      Alert.alert('Error', 'No se pudo unir al SAN');
    } finally {
      setJoining(false);
    }
  };

  const handleViewComments = () => {
    navigation.navigate('Comments', { contentId: sanId, contentType: 'san' });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'activo':
        return '#10B981';
      case 'finalizado':
        return '#3B82F6';
      case 'cancelado':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getTurnStatusColor = (status: string) => {
    switch (status) {
      case 'cumplido':
        return '#10B981';
      case 'activo':
        return '#F59E0B';
      case 'pendiente':
        return '#6B7280';
      default:
        return '#6B7280';
    }
  };

  const getPaymentStatusColor = (status: string) => {
    switch (status) {
      case 'exitoso':
        return '#10B981';
      case 'pendiente':
        return '#F59E0B';
      case 'fallido':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Cargando SAN...</Text>
      </View>
    );
  }

  if (!san) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>No se pudo cargar el SAN</Text>
      </View>
    );
  }

  const userTurn = turnos.find(t => t.participante.usuario.id === user?.id);
  const nextTurn = turnos.find(t => t.estado === 'pendiente');
  const totalCollected = pagos.filter(p => p.estado === 'exitoso').reduce((sum, p) => sum + p.monto, 0);
  const progressPercentage = (totalCollected / san.precio_total) * 100;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>← Volver</Text>
        </TouchableOpacity>
        
        <View style={styles.headerContent}>
          <Text style={styles.sanName}>{san.nombre}</Text>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(san.estado) }]}>
            <Text style={styles.statusText}>{san.estado.toUpperCase()}</Text>
          </View>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressHeader}>
          <Text style={styles.progressTitle}>Progreso del SAN</Text>
          <Text style={styles.progressPercentage}>{progressPercentage.toFixed(1)}%</Text>
        </View>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progressPercentage}%` }]} />
        </View>
        <View style={styles.progressDetails}>
          <Text style={styles.progressText}>
            Recaudado: {formatCurrency(totalCollected)}
          </Text>
          <Text style={styles.progressText}>
            Meta: {formatCurrency(san.precio_total)}
          </Text>
        </View>
      </View>

      {/* Action Button */}
      {!participacion && san.estado === 'activo' && (
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={[styles.joinButton, joining && styles.joinButtonDisabled]}
            onPress={handleJoinSan}
            disabled={joining}
          >
            <Text style={styles.joinButtonText}>
              {joining ? 'Uniéndose...' : 'Unirse al SAN'}
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'info' && styles.activeTab]}
          onPress={() => setActiveTab('info')}
        >
          <Text style={[styles.tabText, activeTab === 'info' && styles.activeTabText]}>
            Información
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'turnos' && styles.activeTab]}
          onPress={() => setActiveTab('turnos')}
        >
          <Text style={[styles.tabText, activeTab === 'turnos' && styles.activeTabText]}>
            Turnos
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'pagos' && styles.activeTab]}
          onPress={() => setActiveTab('pagos')}
        >
          <Text style={[styles.tabText, activeTab === 'pagos' && styles.activeTabText]}>
            Pagos
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'comentarios' && styles.activeTab]}
          onPress={() => setActiveTab('comentarios')}
        >
          <Text style={[styles.tabText, activeTab === 'comentarios' && styles.activeTabText]}>
            Comentarios ({comentarios.length})
          </Text>
        </TouchableOpacity>
      </View>

      {/* Tab Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {activeTab === 'info' && (
          <View style={styles.tabContent}>
            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Descripción</Text>
              <Text style={styles.infoDescription}>{san.descripcion}</Text>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Detalles Financieros</Text>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Cuota semanal:</Text>
                <Text style={styles.infoValue}>{formatCurrency(san.precio_cuota)}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Total a recaudar:</Text>
                <Text style={styles.infoValue}>{formatCurrency(san.precio_total)}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Número de cuotas:</Text>
                <Text style={styles.infoValue}>{san.numero_cuotas}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Frecuencia:</Text>
                <Text style={styles.infoValue}>{san.frecuencia}</Text>
              </View>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Participantes</Text>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Actuales:</Text>
                <Text style={styles.infoValue}>{san.participantes_count}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Máximo:</Text>
                <Text style={styles.infoValue}>{san.max_participantes}</Text>
              </View>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Fechas</Text>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Inicio:</Text>
                <Text style={styles.infoValue}>{formatDate(san.fecha_inicio)}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Fin estimado:</Text>
                <Text style={styles.infoValue}>{formatDate(san.fecha_fin)}</Text>
              </View>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Organizador</Text>
              <Text style={styles.infoValue}>{san.organizador.username}</Text>
            </View>

            {participacion && (
              <View style={styles.infoCard}>
                <Text style={styles.infoTitle}>Tu Participación</Text>
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Orden de cobro:</Text>
                  <Text style={styles.infoValue}>{participacion.orden_cobro}</Text>
                </View>
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Cuotas pagadas:</Text>
                  <Text style={styles.infoValue}>{participacion.cuotas_pagadas}</Text>
                </View>
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>Fecha de inscripción:</Text>
                  <Text style={styles.infoValue}>{formatDate(participacion.fecha_inscripcion)}</Text>
                </View>
              </View>
            )}
          </View>
        )}

        {activeTab === 'turnos' && (
          <View style={styles.tabContent}>
            {turnos.length > 0 ? (
              turnos.map((turno) => (
                <View key={turno.id} style={styles.turnCard}>
                  <View style={styles.turnHeader}>
                    <Text style={styles.turnNumber}>Turno #{turno.numero_turno}</Text>
                    <View style={[styles.turnStatus, { backgroundColor: getTurnStatusColor(turno.estado) }]}>
                      <Text style={styles.turnStatusText}>{turno.estado.toUpperCase()}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.turnDetails}>
                    <Text style={styles.turnParticipant}>
                      Participante: {turno.participante.usuario.username}
                    </Text>
                    <Text style={styles.turnAmount}>
                      Monto: {formatCurrency(turno.monto_turno)}
                    </Text>
                    {turno.fecha_activacion && (
                      <Text style={styles.turnDate}>
                        Activado: {formatDate(turno.fecha_activacion)}
                      </Text>
                    )}
                    {turno.fecha_cumplimiento && (
                      <Text style={styles.turnDate}>
                        Cumplido: {formatDate(turno.fecha_cumplimiento)}
                      </Text>
                    )}
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No hay turnos asignados aún</Text>
              </View>
            )}
          </View>
        )}

        {activeTab === 'pagos' && (
          <View style={styles.tabContent}>
            {pagos.length > 0 ? (
              pagos.map((pago) => (
                <View key={pago.id} style={styles.paymentCard}>
                  <View style={styles.paymentHeader}>
                    <Text style={styles.paymentCode}>{pago.codigo_transaccion}</Text>
                    <View style={[styles.paymentStatus, { backgroundColor: getPaymentStatusColor(pago.estado) }]}>
                      <Text style={styles.paymentStatusText}>{pago.estado.toUpperCase()}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.paymentDetails}>
                    <Text style={styles.paymentUser}>
                      Usuario: {pago.usuario.username}
                    </Text>
                    <Text style={styles.paymentAmount}>
                      Monto: {formatCurrency(pago.monto)}
                    </Text>
                    <Text style={styles.paymentMethod}>
                      Método: {pago.metodo_pago}
                    </Text>
                    <Text style={styles.paymentDate}>
                      Fecha: {formatDate(pago.fecha_creacion)}
                    </Text>
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No hay pagos registrados</Text>
              </View>
            )}
          </View>
        )}

        {activeTab === 'comentarios' && (
          <View style={styles.tabContent}>
            <View style={styles.commentsHeader}>
              <Text style={styles.commentsTitle}>Comentarios ({comentarios.length})</Text>
              <TouchableOpacity
                style={styles.addCommentButton}
                onPress={handleViewComments}
              >
                <Text style={styles.addCommentButtonText}>Ver todos</Text>
              </TouchableOpacity>
            </View>

            {comentarios.length > 0 ? (
              comentarios.slice(0, 3).map((comentario) => (
                <View key={comentario.id} style={styles.commentCard}>
                  <View style={styles.commentHeader}>
                    <Text style={styles.commentUser}>{comentario.usuario.username}</Text>
                    <Text style={styles.commentDate}>
                      {formatDate(comentario.fecha_creacion)}
                    </Text>
                  </View>
                  <Text style={styles.commentText}>{comentario.texto}</Text>
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No hay comentarios aún</Text>
                <TouchableOpacity
                  style={styles.addCommentButton}
                  onPress={handleViewComments}
                >
                  <Text style={styles.addCommentButtonText}>Agregar primer comentario</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
  },
  loadingText: {
    fontSize: 18,
    color: '#64748B',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
  },
  errorText: {
    fontSize: 18,
    color: '#EF4444',
  },
  header: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    paddingTop: 40,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backButton: {
    marginBottom: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#3B82F6',
    fontWeight: '600',
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sanName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1E293B',
    flex: 1,
    marginRight: 16,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    minWidth: 100,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  progressContainer: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E293B',
  },
  progressPercentage: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E2E8F0',
    borderRadius: 4,
    marginBottom: 12,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: 4,
  },
  progressDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  progressText: {
    fontSize: 14,
    color: '#64748B',
  },
  actionContainer: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  joinButton: {
    backgroundColor: '#10B981',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  joinButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  joinButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginHorizontal: 2,
    borderRadius: 8,
    backgroundColor: '#F1F5F9',
  },
  activeTab: {
    backgroundColor: '#3B82F6',
  },
  tabText: {
    textAlign: 'center',
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  activeTabText: {
    color: '#FFFFFF',
  },
  content: {
    flex: 1,
  },
  tabContent: {
    padding: 20,
  },
  infoCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 12,
  },
  infoDescription: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: '#64748B',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  turnCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  turnHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  turnNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  turnStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
  },
  turnStatusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  turnDetails: {
    gap: 8,
  },
  turnParticipant: {
    fontSize: 14,
    color: '#64748B',
  },
  turnAmount: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  turnDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  paymentCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  paymentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  paymentCode: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
  },
  paymentStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
  },
  paymentStatusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  paymentDetails: {
    gap: 8,
  },
  paymentUser: {
    fontSize: 14,
    color: '#64748B',
  },
  paymentAmount: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  paymentMethod: {
    fontSize: 14,
    color: '#64748B',
  },
  paymentDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  commentsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  commentsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  addCommentButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  addCommentButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  commentCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  commentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  commentUser: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
  },
  commentDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  commentText: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 16,
  },
});

export default SanDetailScreen;
