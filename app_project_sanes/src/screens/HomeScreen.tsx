import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Image,
  Dimensions,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { San, Rifa } from '../types';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

const { width } = Dimensions.get('window');

const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const { user } = useAuth();
  
  const [sanes, setSanes] = useState<San[]>([]);
  const [rifas, setRifas] = useState<Rifa[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'sanes' | 'rifas'>('sanes');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Cargar SANes activos
      const sanesResponse = await apiService.getSanes({ estado: 'activo' });
      if (sanesResponse.success && sanesResponse.data) {
        setSanes(sanesResponse.data.results || []);
      }

      // Cargar rifas activas
      const rifasResponse = await apiService.getRifas({ estado: 'activa' });
      if (rifasResponse.success && rifasResponse.data) {
        setRifas(rifasResponse.data.results || []);
      }
    } catch (error) {
      console.error('Error loading data:', error);
      Alert.alert('Error', 'No se pudieron cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleSanPress = (san: San) => {
    navigation.navigate('SanDetail', { sanId: san.id });
  };

  const handleRifaPress = (rifa: Rifa) => {
    navigation.navigate('RifaDetail', { rifaId: rifa.id });
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
      case 'activa':
        return '#10B981';
      case 'finalizado':
      case 'finalizada':
        return '#3B82F6';
      case 'cancelado':
      case 'cancelada':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'activo':
      case 'activa':
        return 'Activo';
      case 'finalizado':
      case 'finalizada':
        return 'Finalizado';
      case 'cancelado':
      case 'cancelada':
        return 'Cancelado';
      default:
        return status;
    }
  };

  const renderSanCard = (san: San) => (
    <TouchableOpacity
      key={san.id}
      style={styles.card}
      onPress={() => handleSanPress(san)}
      activeOpacity={0.7}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle} numberOfLines={2}>
          {san.nombre}
        </Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(san.estado) }]}>
          <Text style={styles.statusText}>{getStatusText(san.estado)}</Text>
        </View>
      </View>

      <Text style={styles.cardDescription} numberOfLines={3}>
        {san.descripcion}
      </Text>

      <View style={styles.cardDetails}>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Cuota:</Text>
          <Text style={styles.detailValue}>{formatCurrency(san.precio_cuota)}</Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Total:</Text>
          <Text style={styles.detailValue}>{formatCurrency(san.precio_total)}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Frecuencia:</Text>
          <Text style={styles.detailValue}>{san.frecuencia}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Participantes:</Text>
          <Text style={styles.detailValue}>
            {san.participantes_count}/{san.max_participantes}
          </Text>
        </View>
      </View>

      <View style={styles.cardFooter}>
        <Text style={styles.organizerText}>
          Organizado por: {san.organizador.username}
        </Text>
        <Text style={styles.dateText}>
          Inicia: {formatDate(san.fecha_inicio)}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const renderRifaCard = (rifa: Rifa) => (
    <TouchableOpacity
      key={rifa.id}
      style={styles.card}
      onPress={() => handleRifaPress(rifa)}
      activeOpacity={0.7}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle} numberOfLines={2}>
          {rifa.titulo}
        </Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(rifa.estado) }]}>
          <Text style={styles.statusText}>{getStatusText(rifa.estado)}</Text>
        </View>
      </View>

      <Text style={styles.cardDescription} numberOfLines={3}>
        {rifa.descripcion}
      </Text>

      <View style={styles.cardDetails}>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Precio ticket:</Text>
          <Text style={styles.detailValue}>{formatCurrency(rifa.precio_ticket)}</Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Tickets disponibles:</Text>
          <Text style={styles.detailValue}>{rifa.tickets_disponibles}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Total tickets:</Text>
          <Text style={styles.detailValue}>{rifa.numero_tickets}</Text>
        </View>
      </View>

      <View style={styles.cardFooter}>
        <Text style={styles.organizerText}>
          Organizado por: {rifa.organizador.username}
        </Text>
        <Text style={styles.dateText}>
          Sorteo: {formatDate(rifa.fecha_fin)}
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Cargando...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.welcomeText}>
          ¡Hola, {user?.first_name || user?.username || 'Usuario'}!
        </Text>
        <Text style={styles.subtitleText}>
          Explora SANes y rifas disponibles
        </Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'sanes' && styles.activeTab]}
          onPress={() => setActiveTab('sanes')}
        >
          <Text style={[styles.tabText, activeTab === 'sanes' && styles.activeTabText]}>
            SANes ({sanes.length})
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'rifas' && styles.activeTab]}
          onPress={() => setActiveTab('rifas')}
        >
          <Text style={[styles.tabText, activeTab === 'rifas' && styles.activeTabText]}>
            Rifas ({rifas.length})
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {activeTab === 'sanes' ? (
          <View style={styles.cardsContainer}>
            {sanes.length > 0 ? (
              sanes.map(renderSanCard)
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>
                  No hay SANes activos disponibles
                </Text>
                <Text style={styles.emptyStateSubtext}>
                  Vuelve más tarde para ver nuevas oportunidades
                </Text>
              </View>
            )}
          </View>
        ) : (
          <View style={styles.cardsContainer}>
            {rifas.length > 0 ? (
              rifas.map(renderRifaCard)
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>
                  No hay rifas activas disponibles
                </Text>
                <Text style={styles.emptyStateSubtext}>
                  Vuelve más tarde para ver nuevas rifas
                </Text>
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
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 4,
  },
  subtitleText: {
    fontSize: 16,
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
    paddingHorizontal: 20,
    marginHorizontal: 4,
    borderRadius: 8,
    backgroundColor: '#F1F5F9',
  },
  activeTab: {
    backgroundColor: '#3B82F6',
  },
  tabText: {
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
    color: '#64748B',
  },
  activeTabText: {
    color: '#FFFFFF',
  },
  content: {
    flex: 1,
  },
  cardsContainer: {
    padding: 20,
  },
  card: {
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
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    flex: 1,
    marginRight: 12,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    minWidth: 80,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
  },
  cardDescription: {
    fontSize: 14,
    color: '#64748B',
    lineHeight: 20,
    marginBottom: 16,
  },
  cardDetails: {
    marginBottom: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#64748B',
    fontWeight: '500',
  },
  detailValue: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
  },
  cardFooter: {
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingTop: 12,
  },
  organizerText: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 4,
  },
  dateText: {
    fontSize: 12,
    color: '#64748B',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
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
  },
});

export default HomeScreen;
