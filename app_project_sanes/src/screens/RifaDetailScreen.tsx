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
  Modal,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { Rifa, Ticket, Comment } from '../types';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

type RifaDetailScreenNavigationProp = StackNavigationProp<RootStackParamList, 'RifaDetail'>;
type RifaDetailScreenRouteProp = RouteProp<RootStackParamList, 'RifaDetail'>;

const { width } = Dimensions.get('window');

const RifaDetailScreen: React.FC = () => {
  const navigation = useNavigation<RifaDetailScreenNavigationProp>();
  const route = useRoute<RifaDetailScreenRouteProp>();
  const { user } = useAuth();
  
  const { rifaId } = route.params;
  
  const [rifa, setRifa] = useState<Rifa | null>(null);
  const [userTickets, setUserTickets] = useState<Ticket[]>([]);
  const [comentarios, setComentarios] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'info' | 'tickets' | 'comentarios'>('info');
  const [buyingTicket, setBuyingTicket] = useState(false);
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [selectedTicketNumber, setSelectedTicketNumber] = useState<number | null>(null);

  useEffect(() => {
    loadRifaData();
  }, [rifaId]);

  const loadRifaData = async () => {
    try {
      setLoading(true);
      
      // Cargar detalles de la rifa
      const rifaResponse = await apiService.getRifaDetail(rifaId);
      if (rifaResponse.success && rifaResponse.data) {
        setRifa(rifaResponse.data);
      }

      // Cargar comentarios de la rifa
      const comentariosResponse = await apiService.getComments('rifa', rifaId);
      if (comentariosResponse.success && comentariosResponse.data) {
        setComentarios(comentariosResponse.data);
      }

      // Cargar tickets del usuario si está autenticado
      if (user) {
        const ticketsResponse = await apiService.getUserTickets();
        if (ticketsResponse.success && ticketsResponse.data) {
          const userRifaTickets = ticketsResponse.data.filter(
            t => t.rifa.id === rifaId
          );
          setUserTickets(userRifaTickets);
        }
      }
    } catch (error) {
      console.error('Error loading rifa data:', error);
      Alert.alert('Error', 'No se pudieron cargar los datos de la rifa');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadRifaData();
    setRefreshing(false);
  };

  const handleBuyTicket = async () => {
    if (!user) {
      Alert.alert('Error', 'Debes iniciar sesión para comprar tickets');
      return;
    }

    if (!rifa || rifa.tickets_disponibles <= 0) {
      Alert.alert('Error', 'No hay tickets disponibles');
      return;
    }

    setShowTicketModal(true);
  };

  const confirmTicketPurchase = async () => {
    if (!selectedTicketNumber) {
      Alert.alert('Error', 'Debes seleccionar un número de ticket');
      return;
    }

    try {
      setBuyingTicket(true);
      const response = await apiService.buyTicket(rifaId, { numero: selectedTicketNumber });
      
      if (response.success && response.data) {
        Alert.alert(
          '¡Éxito!',
          `Has comprado el ticket #${selectedTicketNumber} exitosamente.`,
          [{ text: 'OK' }]
        );
        
        // Recargar datos
        await loadRifaData();
        setShowTicketModal(false);
        setSelectedTicketNumber(null);
      } else {
        Alert.alert('Error', response.message || 'No se pudo comprar el ticket');
      }
    } catch (error) {
      console.error('Error buying ticket:', error);
      Alert.alert('Error', 'No se pudo comprar el ticket');
    } finally {
      setBuyingTicket(false);
    }
  };

  const handleViewComments = () => {
    navigation.navigate('Comments', { contentId: rifaId, contentType: 'rifa' });
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
      case 'activa':
        return '#10B981';
      case 'finalizada':
        return '#3B82F6';
      case 'cancelada':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getTicketStatusColor = (status: string) => {
    switch (status) {
      case 'activo':
        return '#10B981';
      case 'pendiente':
        return '#F59E0B';
      case 'cancelado':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Cargando rifa...</Text>
      </View>
    );
  }

  if (!rifa) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>No se pudo cargar la rifa</Text>
      </View>
    );
  }

  const availableTicketNumbers = Array.from(
    { length: rifa.tickets_disponibles },
    (_, i) => i + 1
  );

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
          <Text style={styles.rifaTitle}>{rifa.titulo}</Text>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(rifa.estado) }]}>
            <Text style={styles.statusText}>{rifa.estado.toUpperCase()}</Text>
          </View>
        </View>
      </View>

      {/* Action Button */}
      {rifa.estado === 'activa' && rifa.tickets_disponibles > 0 && (
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={[styles.buyButton, buyingTicket && styles.buyButtonDisabled]}
            onPress={handleBuyTicket}
            disabled={buyingTicket}
          >
            <Text style={styles.buyButtonText}>
              {buyingTicket ? 'Comprando...' : `Comprar Ticket - ${formatCurrency(rifa.precio_ticket)}`}
            </Text>
          </TouchableOpacity>
          <Text style={styles.ticketsAvailable}>
            {rifa.tickets_disponibles} tickets disponibles
          </Text>
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
          style={[styles.tab, activeTab === 'tickets' && styles.activeTab]}
          onPress={() => setActiveTab('tickets')}
        >
          <Text style={[styles.tabText, activeTab === 'tickets' && styles.activeTabText]}>
            Mis Tickets ({userTickets.length})
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
              <Text style={styles.infoDescription}>{rifa.descripcion}</Text>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Detalles del Ticket</Text>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Precio por ticket:</Text>
                <Text style={styles.infoValue}>{formatCurrency(rifa.precio_ticket)}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Tickets disponibles:</Text>
                <Text style={styles.infoValue}>{rifa.tickets_disponibles}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Total de tickets:</Text>
                <Text style={styles.infoValue}>{rifa.numero_tickets}</Text>
              </View>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Fechas</Text>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Inicio:</Text>
                <Text style={styles.infoValue}>{formatDate(rifa.fecha_inicio)}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Sorteo:</Text>
                <Text style={styles.infoValue}>{formatDate(rifa.fecha_fin)}</Text>
              </View>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Organizador</Text>
              <Text style={styles.infoValue}>{rifa.organizador.username}</Text>
            </View>

            {rifa.ganador && (
              <View style={styles.infoCard}>
                <Text style={styles.infoTitle}>Ganador</Text>
                <Text style={styles.infoValue}>{rifa.ganador.username}</Text>
              </View>
            )}
          </View>
        )}

        {activeTab === 'tickets' && (
          <View style={styles.tabContent}>
            {userTickets.length > 0 ? (
              userTickets.map((ticket) => (
                <View key={ticket.id} style={styles.ticketCard}>
                  <View style={styles.ticketHeader}>
                    <Text style={styles.ticketNumber}>Ticket #{ticket.numero}</Text>
                    <View style={[styles.ticketStatus, { backgroundColor: getTicketStatusColor(ticket.estado) }]}>
                      <Text style={styles.ticketStatusText}>{ticket.estado.toUpperCase()}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.ticketDetails}>
                    <Text style={styles.ticketPrice}>
                      Precio pagado: {formatCurrency(ticket.precio_pagado)}
                    </Text>
                    <Text style={styles.ticketDate}>
                      Fecha de compra: {formatDate(ticket.fecha_compra)}
                    </Text>
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No has comprado tickets de esta rifa</Text>
                {rifa.estado === 'activa' && (
                  <TouchableOpacity
                    style={styles.buyFirstTicketButton}
                    onPress={handleBuyTicket}
                  >
                    <Text style={styles.buyFirstTicketButtonText}>Comprar primer ticket</Text>
                  </TouchableOpacity>
                )}
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

      {/* Ticket Selection Modal */}
      <Modal
        visible={showTicketModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowTicketModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Seleccionar Número de Ticket</Text>
            <Text style={styles.modalSubtitle}>
              Elige el número de ticket que deseas comprar
            </Text>
            
            <ScrollView style={styles.ticketNumbersContainer} showsVerticalScrollIndicator={false}>
              <View style={styles.ticketNumbersGrid}>
                {availableTicketNumbers.map((number) => (
                  <TouchableOpacity
                    key={number}
                    style={[
                      styles.ticketNumberButton,
                      selectedTicketNumber === number && styles.selectedTicketNumber
                    ]}
                    onPress={() => setSelectedTicketNumber(number)}
                  >
                    <Text style={[
                      styles.ticketNumberButtonText,
                      selectedTicketNumber === number && styles.selectedTicketNumberText
                    ]}>
                      {number}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => {
                  setShowTicketModal(false);
                  setSelectedTicketNumber(null);
                }}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[
                  styles.confirmButton,
                  !selectedTicketNumber && styles.confirmButtonDisabled
                ]}
                onPress={confirmTicketPurchase}
                disabled={!selectedTicketNumber || buyingTicket}
              >
                <Text style={styles.confirmButtonText}>
                  {buyingTicket ? 'Comprando...' : 'Confirmar Compra'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  rifaTitle: {
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
  actionContainer: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    alignItems: 'center',
  },
  buyButton: {
    backgroundColor: '#10B981',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 8,
    marginBottom: 12,
  },
  buyButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  buyButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  ticketsAvailable: {
    fontSize: 14,
    color: '#64748B',
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
  ticketCard: {
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
  ticketHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  ticketNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  ticketStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
  },
  ticketStatusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  ticketDetails: {
    gap: 8,
  },
  ticketPrice: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  ticketDate: {
    fontSize: 14,
    color: '#64748B',
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
  buyFirstTicketButton: {
    backgroundColor: '#10B981',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buyFirstTicketButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    margin: 20,
    maxHeight: '80%',
    width: '90%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1E293B',
    textAlign: 'center',
    marginBottom: 8,
  },
  modalSubtitle: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 24,
  },
  ticketNumbersContainer: {
    maxHeight: 300,
    marginBottom: 24,
  },
  ticketNumbersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  ticketNumberButton: {
    width: 60,
    height: 60,
    backgroundColor: '#F1F5F9',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  selectedTicketNumber: {
    backgroundColor: '#3B82F6',
  },
  ticketNumberButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#64748B',
  },
  selectedTicketNumberText: {
    color: '#FFFFFF',
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#64748B',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButton: {
    flex: 1,
    backgroundColor: '#10B981',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  confirmButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default RifaDetailScreen;
