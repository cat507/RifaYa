import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Image,
  Modal,
  TextInput,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { User, Ticket, ParticipacionSan, Factura } from '../types';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

type ProfileScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Profile'>;

const ProfileScreen: React.FC = () => {
  const navigation = useNavigation<ProfileScreenNavigationProp>();
  const { user, updateUser, logout } = useAuth();
  
  const [userTickets, setUserTickets] = useState<Ticket[]>([]);
  const [userParticipations, setUserParticipations] = useState<ParticipacionSan[]>([]);
  const [userFacturas, setUserFacturas] = useState<Factura[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'tickets' | 'sanes' | 'facturas'>('profile');
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState<Partial<User>>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      loadUserData();
    }
  }, [user]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      
      // Cargar tickets del usuario
      const ticketsResponse = await apiService.getUserTickets();
      if (ticketsResponse.success && ticketsResponse.data) {
        setUserTickets(ticketsResponse.data);
      }

      // Cargar participaciones del usuario
      const participationsResponse = await apiService.getUserParticipations();
      if (participationsResponse.success && participationsResponse.data) {
        setUserParticipations(participationsResponse.data);
      }

      // Cargar facturas del usuario
      const facturasResponse = await apiService.getUserFacturas();
      if (facturasResponse.success && facturasResponse.data) {
        setUserFacturas(facturasResponse.data);
      }
    } catch (error) {
      console.error('Error loading user data:', error);
      Alert.alert('Error', 'No se pudieron cargar los datos del usuario');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadUserData();
    setRefreshing(false);
  };

  const handleEditProfile = () => {
    if (user) {
      setEditingUser({
        first_name: user.first_name,
        last_name: user.last_name,
        phone_number: user.phone_number || '',
        cedula: user.cedula || '',
        oficio: user.oficio || '',
      });
      setShowEditModal(true);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      await updateUser(editingUser);
      setShowEditModal(false);
      Alert.alert('Éxito', 'Perfil actualizado correctamente');
    } catch (error) {
      console.error('Error updating profile:', error);
      Alert.alert('Error', 'No se pudo actualizar el perfil');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Cerrar Sesión',
      '¿Estás seguro de que quieres cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Cerrar Sesión', style: 'destructive', onPress: logout },
      ]
    );
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

  const getFacturaStatusColor = (status: string) => {
    switch (status) {
      case 'confirmado':
        return '#10B981';
      case 'pendiente':
        return '#F59E0B';
      case 'rechazado':
        return '#EF4444';
      case 'cancelado':
        return '#6B7280';
      default:
        return '#6B7280';
    }
  };

  if (!user) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Usuario no autenticado</Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Cargando perfil...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mi Perfil</Text>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Cerrar Sesión</Text>
        </TouchableOpacity>
      </View>

      {/* User Info Card */}
      <View style={styles.userCard}>
        <View style={styles.userAvatar}>
          {user.foto_perfil ? (
            <Image source={{ uri: user.foto_perfil }} style={styles.avatarImage} />
          ) : (
            <View style={styles.avatarPlaceholder}>
              <Text style={styles.avatarText}>
                {user.first_name ? user.first_name[0].toUpperCase() : user.username[0].toUpperCase()}
              </Text>
            </View>
          )}
        </View>
        
        <View style={styles.userInfo}>
          <Text style={styles.userName}>
            {user.first_name && user.last_name
              ? `${user.first_name} ${user.last_name}`
              : user.username}
          </Text>
          <Text style={styles.userEmail}>{user.email}</Text>
          <Text style={styles.userUsername}>@{user.username}</Text>
        </View>

        <TouchableOpacity style={styles.editButton} onPress={handleEditProfile}>
          <Text style={styles.editButtonText}>Editar</Text>
        </TouchableOpacity>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{userTickets.length}</Text>
          <Text style={styles.statLabel}>Tickets</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{userParticipations.length}</Text>
          <Text style={styles.statLabel}>SANes</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{userFacturas.length}</Text>
          <Text style={styles.statLabel}>Facturas</Text>
        </View>
        
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{user.reputacion || 0}</Text>
          <Text style={styles.statLabel}>Reputación</Text>
        </View>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'profile' && styles.activeTab]}
          onPress={() => setActiveTab('profile')}
        >
          <Text style={[styles.tabText, activeTab === 'profile' && styles.activeTabText]}>
            Perfil
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'tickets' && styles.activeTab]}
          onPress={() => setActiveTab('tickets')}
        >
          <Text style={[styles.tabText, activeTab === 'tickets' && styles.activeTabText]}>
            Tickets
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'sanes' && styles.activeTab]}
          onPress={() => setActiveTab('sanes')}
        >
          <Text style={[styles.tabText, activeTab === 'sanes' && styles.activeTabText]}>
            SANes
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'facturas' && styles.activeTab]}
          onPress={() => setActiveTab('facturas')}
        >
          <Text style={[styles.tabText, activeTab === 'facturas' && styles.activeTabText]}>
            Facturas
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
        {activeTab === 'profile' && (
          <View style={styles.tabContent}>
            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Información Personal</Text>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Nombre completo:</Text>
                <Text style={styles.infoValue}>
                  {user.first_name && user.last_name
                    ? `${user.first_name} ${user.last_name}`
                    : 'No especificado'}
                </Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Teléfono:</Text>
                <Text style={styles.infoValue}>
                  {user.phone_number || 'No especificado'}
                </Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Cédula:</Text>
                <Text style={styles.infoValue}>
                  {user.cedula || 'No especificado'}
                </Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Oficio:</Text>
                <Text style={styles.infoValue}>
                  {user.oficio || 'No especificado'}
                </Text>
              </View>
            </View>

            <View style={styles.infoCard}>
              <Text style={styles.infoTitle}>Información de Cuenta</Text>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Usuario:</Text>
                <Text style={styles.infoValue}>{user.username}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Email:</Text>
                <Text style={styles.infoValue}>{user.email}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Fecha de registro:</Text>
                <Text style={styles.infoValue}>{formatDate(user.date_joined)}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Último acceso:</Text>
                <Text style={styles.infoValue}>{formatDate(user.last_login)}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Estado:</Text>
                <Text style={[styles.infoValue, { color: user.is_active ? '#10B981' : '#EF4444' }]}>
                  {user.is_active ? 'Activo' : 'Inactivo'}
                </Text>
              </View>
            </View>
          </View>
        )}

        {activeTab === 'tickets' && (
          <View style={styles.tabContent}>
            {userTickets.length > 0 ? (
              userTickets.map((ticket) => (
                <View key={ticket.id} style={styles.ticketCard}>
                  <View style={styles.ticketHeader}>
                    <Text style={styles.ticketTitle}>{ticket.rifa.titulo}</Text>
                    <View style={[styles.ticketStatus, { backgroundColor: getTicketStatusColor(ticket.estado) }]}>
                      <Text style={styles.ticketStatusText}>{ticket.estado.toUpperCase()}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.ticketDetails}>
                    <Text style={styles.ticketNumber}>Ticket #{ticket.numero}</Text>
                    <Text style={styles.ticketPrice}>
                      Precio: {formatCurrency(ticket.precio_pagado)}
                    </Text>
                    <Text style={styles.ticketDate}>
                      Comprado: {formatDate(ticket.fecha_compra)}
                    </Text>
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No has comprado tickets aún</Text>
                <Text style={styles.emptyStateSubtext}>
                  Explora las rifas disponibles para comprar tu primer ticket
                </Text>
              </View>
            )}
          </View>
        )}

        {activeTab === 'sanes' && (
          <View style={styles.tabContent}>
            {userParticipations.length > 0 ? (
              userParticipations.map((participacion) => (
                <View key={participacion.id} style={styles.sanCard}>
                  <View style={styles.sanHeader}>
                    <Text style={styles.sanTitle}>{participacion.san.nombre}</Text>
                    <View style={[styles.sanStatus, { backgroundColor: '#3B82F6' }]}>
                      <Text style={styles.sanStatusText}>{participacion.estado.toUpperCase()}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.sanDetails}>
                    <Text style={styles.sanOrder}>Orden de cobro: #{participacion.orden_cobro}</Text>
                    <Text style={styles.sanCuotas}>
                      Cuotas pagadas: {participacion.cuotas_pagadas}/{participacion.san.numero_cuotas}
                    </Text>
                    <Text style={styles.sanDate}>
                      Inscrito: {formatDate(participacion.fecha_inscripcion)}
                    </Text>
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No participas en SANes aún</Text>
                <Text style={styles.emptyStateSubtext}>
                  Explora los SANes disponibles para unirte
                </Text>
              </View>
            )}
          </View>
        )}

        {activeTab === 'facturas' && (
          <View style={styles.tabContent}>
            {userFacturas.length > 0 ? (
              userFacturas.map((factura) => (
                <View key={factura.id} style={styles.facturaCard}>
                  <View style={styles.facturaHeader}>
                    <Text style={styles.facturaCode}>{factura.codigo}</Text>
                    <View style={[styles.facturaStatus, { backgroundColor: getFacturaStatusColor(factura.estado_pago) }]}>
                      <Text style={styles.facturaStatusText}>{factura.estado_pago.toUpperCase()}</Text>
                    </View>
                  </View>
                  
                  <View style={styles.facturaDetails}>
                    <Text style={styles.facturaType}>Tipo: {factura.tipo}</Text>
                    <Text style={styles.facturaAmount}>
                      Monto: {formatCurrency(factura.monto_total)}
                    </Text>
                    <Text style={styles.facturaDate}>
                      Emitida: {formatDate(factura.fecha_emision)}
                    </Text>
                    {factura.fecha_pago && (
                      <Text style={styles.facturaDate}>
                        Pagada: {formatDate(factura.fecha_pago)}
                      </Text>
                    )}
                  </View>
                </View>
              ))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No tienes facturas aún</Text>
                <Text style={styles.emptyStateSubtext}>
                  Las facturas aparecerán cuando compres tickets o te unas a SANes
                </Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      {/* Edit Profile Modal */}
      <Modal
        visible={showEditModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowEditModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Editar Perfil</Text>
            
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Nombre</Text>
              <TextInput
                style={styles.textInput}
                value={editingUser.first_name}
                onChangeText={(text) => setEditingUser({ ...editingUser, first_name: text })}
                placeholder="Nombre"
              />
            </View>
            
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Apellido</Text>
              <TextInput
                style={styles.textInput}
                value={editingUser.last_name}
                onChangeText={(text) => setEditingUser({ ...editingUser, last_name: text })}
                placeholder="Apellido"
              />
            </View>
            
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Teléfono</Text>
              <TextInput
                style={styles.textInput}
                value={editingUser.phone_number}
                onChangeText={(text) => setEditingUser({ ...editingUser, phone_number: text })}
                placeholder="Teléfono"
                keyboardType="phone-pad"
              />
            </View>
            
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Cédula</Text>
              <TextInput
                style={styles.textInput}
                value={editingUser.cedula}
                onChangeText={(text) => setEditingUser({ ...editingUser, cedula: text })}
                placeholder="Cédula"
              />
            </View>
            
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Oficio</Text>
              <TextInput
                style={styles.textInput}
                value={editingUser.oficio}
                onChangeText={(text) => setEditingUser({ ...editingUser, oficio: text })}
                placeholder="Oficio"
              />
            </View>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setShowEditModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.saveButton, saving && styles.saveButtonDisabled]}
                onPress={handleSaveProfile}
                disabled={saving}
              >
                <Text style={styles.saveButtonText}>
                  {saving ? 'Guardando...' : 'Guardar'}
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  logoutButton: {
    backgroundColor: '#EF4444',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  logoutButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  userCard: {
    backgroundColor: '#FFFFFF',
    margin: 20,
    padding: 20,
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  userAvatar: {
    marginRight: 16,
  },
  avatarImage: {
    width: 60,
    height: 60,
    borderRadius: 30,
  },
  avatarPlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#64748B',
    marginBottom: 2,
  },
  userUsername: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '500',
  },
  editButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  editButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginHorizontal: 4,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3B82F6',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '500',
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
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
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
  ticketTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    flex: 1,
    marginRight: 12,
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
  ticketNumber: {
    fontSize: 14,
    color: '#64748B',
  },
  ticketPrice: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  ticketDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  sanCard: {
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
  sanHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sanTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    flex: 1,
    marginRight: 12,
  },
  sanStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
  },
  sanStatusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  sanDetails: {
    gap: 8,
  },
  sanOrder: {
    fontSize: 14,
    color: '#64748B',
  },
  sanCuotas: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  sanDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  facturaCard: {
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
  facturaHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  facturaCode: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    flex: 1,
    marginRight: 12,
  },
  facturaStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
  },
  facturaStatusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  facturaDetails: {
    gap: 8,
  },
  facturaType: {
    fontSize: 14,
    color: '#64748B',
  },
  facturaAmount: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  facturaDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
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
    width: '90%',
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1E293B',
    textAlign: 'center',
    marginBottom: 24,
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#FFFFFF',
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
    marginTop: 24,
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
  saveButton: {
    flex: 1,
    backgroundColor: '#10B981',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProfileScreen;
