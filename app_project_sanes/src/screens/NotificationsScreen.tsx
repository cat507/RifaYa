import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { NotificacionMejorada } from '../types';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

type NotificationsScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Notifications'>;

const NotificationsScreen: React.FC = () => {
  const navigation = useNavigation<NotificationsScreenNavigationProp>();
  const { user } = useAuth();
  
  const [notifications, setNotifications] = useState<NotificacionMejorada[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeFilter, setActiveFilter] = useState<'all' | 'unread' | 'read'>('all');

  useEffect(() => {
    if (user) {
      loadNotifications();
    }
  }, [user]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await apiService.getNotifications();
      
      if (response.success && response.data) {
        setNotifications(response.data);
      } else {
        console.error('Error loading notifications:', response.message);
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
      Alert.alert('Error', 'No se pudieron cargar las notificaciones');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadNotifications();
    setRefreshing(false);
  };

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      const response = await apiService.markNotificationAsRead(notificationId);
      
      if (response.success && response.data) {
        // Actualizar la notificación local
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? { ...notif, leido: true, fecha_lectura: new Date().toISOString() }
              : notif
          )
        );
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      const response = await apiService.markAllNotificationsAsRead();
      
      if (response.success) {
        // Marcar todas las notificaciones como leídas localmente
        setNotifications(prev => 
          prev.map(notif => ({
            ...notif,
            leido: true,
            fecha_lectura: new Date().toISOString()
          }))
        );
        Alert.alert('Éxito', 'Todas las notificaciones han sido marcadas como leídas');
      }
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      Alert.alert('Error', 'No se pudieron marcar todas las notificaciones como leídas');
    }
  };

  const getNotificationIcon = (tipo: string) => {
    switch (tipo) {
      case 'pago':
        return '💰';
      case 'turno':
        return '⏰';
      case 'comentario':
        return '💬';
      case 'admin':
        return '👨‍💼';
      case 'sistema':
        return '🔔';
      default:
        return '📢';
    }
  };

  const getNotificationColor = (tipo: string) => {
    switch (tipo) {
      case 'pago':
        return '#10B981';
      case 'turno':
        return '#F59E0B';
      case 'comentario':
        return '#3B82F6';
      case 'admin':
        return '#8B5CF6';
      case 'sistema':
        return '#6B7280';
      default:
        return '#3B82F6';
    }
  };

  const getPriorityColor = (prioridad: string) => {
    switch (prioridad) {
      case 'urgente':
        return '#EF4444';
      case 'alta':
        return '#F59E0B';
      case 'media':
        return '#3B82F6';
      case 'baja':
        return '#10B981';
      default:
        return '#6B7280';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Hace unos minutos';
    } else if (diffInHours < 24) {
      return `Hace ${diffInHours} hora${diffInHours > 1 ? 's' : ''}`;
    } else {
      return date.toLocaleDateString('es-CO', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    if (activeFilter === 'unread') return !notification.leido;
    if (activeFilter === 'read') return notification.leido;
    return true;
  });

  const unreadCount = notifications.filter(n => !n.leido).length;

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
        <Text style={styles.loadingText}>Cargando notificaciones...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Notificaciones</Text>
        {unreadCount > 0 && (
          <View style={styles.unreadBadge}>
            <Text style={styles.unreadCount}>{unreadCount}</Text>
          </View>
        )}
      </View>

      {/* Actions */}
      <View style={styles.actionsContainer}>
        <View style={styles.filterContainer}>
          <TouchableOpacity
            style={[styles.filterButton, activeFilter === 'all' && styles.activeFilterButton]}
            onPress={() => setActiveFilter('all')}
          >
            <Text style={[styles.filterButtonText, activeFilter === 'all' && styles.activeFilterButtonText]}>
              Todas ({notifications.length})
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.filterButton, activeFilter === 'unread' && styles.activeFilterButton]}
            onPress={() => setActiveFilter('unread')}
          >
            <Text style={[styles.filterButtonText, activeFilter === 'unread' && styles.activeFilterButtonText]}>
              No leídas ({unreadCount})
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.filterButton, activeFilter === 'read' && styles.activeFilterButton]}
            onPress={() => setActiveFilter('read')}
          >
            <Text style={[styles.filterButtonText, activeFilter === 'read' && styles.activeFilterButtonText]}>
              Leídas ({notifications.length - unreadCount})
            </Text>
          </TouchableOpacity>
        </View>

        {unreadCount > 0 && (
          <TouchableOpacity style={styles.markAllReadButton} onPress={handleMarkAllAsRead}>
            <Text style={styles.markAllReadButtonText}>Marcar todas como leídas</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Notifications List */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {filteredNotifications.length > 0 ? (
          filteredNotifications.map((notification) => (
            <TouchableOpacity
              key={notification.id}
              style={[
                styles.notificationCard,
                !notification.leido && styles.unreadNotificationCard
              ]}
              onPress={() => handleMarkAsRead(notification.id)}
              activeOpacity={0.7}
            >
              <View style={styles.notificationHeader}>
                <View style={styles.notificationIconContainer}>
                  <Text style={styles.notificationIcon}>
                    {getNotificationIcon(notification.tipo)}
                  </Text>
                </View>
                
                <View style={styles.notificationInfo}>
                  <Text style={styles.notificationTitle} numberOfLines={2}>
                    {notification.titulo}
                  </Text>
                  <Text style={styles.notificationMessage} numberOfLines={3}>
                    {notification.mensaje}
                  </Text>
                </View>

                <View style={styles.notificationMeta}>
                  <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(notification.prioridad) }]}>
                    <Text style={styles.priorityText}>{notification.prioridad.toUpperCase()}</Text>
                  </View>
                  
                  <Text style={styles.notificationDate}>
                    {formatDate(notification.fecha_creacion)}
                  </Text>
                </View>
              </View>

              <View style={styles.notificationFooter}>
                <View style={styles.notificationType}>
                  <View style={[styles.typeBadge, { backgroundColor: getNotificationColor(notification.tipo) }]}>
                    <Text style={styles.typeText}>{notification.tipo.toUpperCase()}</Text>
                  </View>
                  
                  <Text style={styles.channelText}>
                    {notification.canal === 'interno' ? '📱 App' : 
                     notification.canal === 'email' ? '📧 Email' :
                     notification.canal === 'whatsapp' ? '📱 WhatsApp' :
                     notification.canal === 'sms' ? '📱 SMS' : '📱 Push'}
                  </Text>
                </View>

                {!notification.leido && (
                  <View style={styles.unreadIndicator}>
                    <View style={styles.unreadDot} />
                    <Text style={styles.unreadText}>No leída</Text>
                  </View>
                )}
              </View>
            </TouchableOpacity>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateIcon}>🔔</Text>
            <Text style={styles.emptyStateText}>
              {activeFilter === 'all' 
                ? 'No tienes notificaciones aún'
                : activeFilter === 'unread'
                ? 'No tienes notificaciones sin leer'
                : 'No tienes notificaciones leídas'}
            </Text>
            <Text style={styles.emptyStateSubtext}>
              {activeFilter === 'all' 
                ? 'Las notificaciones aparecerán aquí cuando tengas actividad en la plataforma'
                : 'Las notificaciones aparecerán aquí cuando las recibas'}
            </Text>
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
  unreadBadge: {
    backgroundColor: '#EF4444',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    minWidth: 24,
    alignItems: 'center',
  },
  unreadCount: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  actionsContainer: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  filterContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginHorizontal: 4,
    borderRadius: 8,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
  },
  activeFilterButton: {
    backgroundColor: '#3B82F6',
  },
  filterButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748B',
  },
  activeFilterButtonText: {
    color: '#FFFFFF',
  },
  markAllReadButton: {
    backgroundColor: '#10B981',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  markAllReadButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  notificationCard: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    marginBottom: 8,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  unreadNotificationCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#3B82F6',
    backgroundColor: '#F8FAFC',
  },
  notificationHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  notificationIconContainer: {
    marginRight: 12,
  },
  notificationIcon: {
    fontSize: 24,
  },
  notificationInfo: {
    flex: 1,
    marginRight: 12,
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
    lineHeight: 20,
  },
  notificationMessage: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 18,
  },
  notificationMeta: {
    alignItems: 'flex-end',
  },
  priorityBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginBottom: 8,
  },
  priorityText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '600',
  },
  notificationDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  notificationFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
  },
  notificationType: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    marginRight: 8,
  },
  typeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '600',
  },
  channelText: {
    fontSize: 12,
    color: '#64748B',
  },
  unreadIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3B82F6',
    marginRight: 6,
  },
  unreadText: {
    fontSize: 12,
    color: '#3B82F6',
    fontWeight: '600',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
    paddingHorizontal: 40,
  },
  emptyStateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default NotificationsScreen;
