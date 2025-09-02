import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  Image,
  Dimensions,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { PaymentForm, PagoSimulado } from '../types';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

type PaymentScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Payment'>;
type PaymentScreenRouteProp = RouteProp<RootStackParamList, 'Payment'>;

const { width } = Dimensions.get('window');

const PaymentScreen: React.FC = () => {
  const navigation = useNavigation<PaymentScreenNavigationProp>();
  const route = useRoute<PaymentScreenRouteProp>();
  const { user } = useAuth();
  
  const { 
    contentId, 
    contentType, 
    amount, 
    description, 
    contentTitle 
  } = route.params;
  
  const [paymentMethod, setPaymentMethod] = useState<'digital' | 'cash'>('digital');
  const [digitalMethod, setDigitalMethod] = useState<'card' | 'paypal' | 'nequi'>('card');
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvv, setCardCvv] = useState('');
  const [cardholderName, setCardholderName] = useState('');
  const [paypalEmail, setPaypalEmail] = useState('');
  const [nequiPhone, setNequiPhone] = useState('');
  const [referenceNumber, setReferenceNumber] = useState('');
  const [paymentProof, setPaymentProof] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [processing, setProcessing] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [paymentResult, setPaymentResult] = useState<PagoSimulado | null>(null);

  useEffect(() => {
    if (user) {
      setCardholderName(user.first_name && user.last_name 
        ? `${user.first_name} ${user.last_name}` 
        : user.username
      );
    }
  }, [user]);

  const validateForm = (): boolean => {
    if (paymentMethod === 'digital') {
      switch (digitalMethod) {
        case 'card':
          if (!cardNumber || !cardExpiry || !cardCvv || !cardholderName) {
            Alert.alert('Error', 'Por favor completa todos los campos de la tarjeta');
            return false;
          }
          if (cardNumber.length < 16) {
            Alert.alert('Error', 'Número de tarjeta inválido');
            return false;
          }
          if (cardExpiry.length !== 5 || !cardExpiry.includes('/')) {
            Alert.alert('Error', 'Fecha de expiración inválida (MM/YY)');
            return false;
          }
          if (cardCvv.length < 3) {
            Alert.alert('Error', 'CVV inválido');
            return false;
          }
          break;
        case 'paypal':
          if (!paypalEmail) {
            Alert.alert('Error', 'Por favor ingresa tu email de PayPal');
            return false;
          }
          break;
        case 'nequi':
          if (!nequiPhone) {
            Alert.alert('Error', 'Por favor ingresa tu número de teléfono');
            return false;
          }
          break;
      }
    } else {
      if (!referenceNumber) {
        Alert.alert('Error', 'Por favor ingresa el número de referencia');
        return false;
      }
    }
    return true;
  };

  const formatCardNumber = (text: string) => {
    const cleaned = text.replace(/\s/g, '');
    const match = cleaned.match(/(\d{1,4})(\d{1,4})?(\d{1,4})?(\d{1,4})?/);
    if (match) {
      const parts = [match[1], match[2], match[3], match[4]].filter(Boolean);
      return parts.join(' ');
    }
    return text;
  };

  const formatExpiry = (text: string) => {
    const cleaned = text.replace(/\D/g, '');
    if (cleaned.length >= 2) {
      return `${cleaned.slice(0, 2)}/${cleaned.slice(2, 4)}`;
    }
    return cleaned;
  };

  const handlePayment = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setProcessing(true);
      
      const paymentData: PaymentForm = {
        monto: amount,
        metodo_pago: paymentMethod === 'digital' ? digitalMethod : 'efectivo',
        referencia: referenceNumber || `${paymentMethod.toUpperCase()}_${Date.now()}`,
        notas: notes,
        comprobante: paymentProof,
      };

      const response = await apiService.createPayment(contentType, contentId, paymentData);
      
      if (response.success && response.data) {
        setPaymentResult(response.data);
        setShowSuccessModal(true);
      } else {
        Alert.alert('Error', response.message || 'No se pudo procesar el pago');
      }
    } catch (error) {
      console.error('Error processing payment:', error);
      Alert.alert('Error', 'No se pudo procesar el pago');
    } finally {
      setProcessing(false);
    }
  };

  const handleSuccessClose = () => {
    setShowSuccessModal(false);
    navigation.navigate('Home');
  };

  const renderDigitalPaymentForm = () => (
    <View style={styles.paymentForm}>
      {/* Método de pago digital */}
      <View style={styles.methodSelector}>
        <Text style={styles.sectionTitle}>Método de Pago Digital</Text>
        <View style={styles.methodButtons}>
          <TouchableOpacity
            style={[styles.methodButton, digitalMethod === 'card' && styles.methodButtonActive]}
            onPress={() => setDigitalMethod('card')}
          >
            <Text style={styles.methodButtonIcon}>💳</Text>
            <Text style={[styles.methodButtonText, digitalMethod === 'card' && styles.methodButtonTextActive]}>
              Tarjeta
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.methodButton, digitalMethod === 'paypal' && styles.methodButtonActive]}
            onPress={() => setDigitalMethod('paypal')}
          >
            <Text style={styles.methodButtonIcon}>📧</Text>
            <Text style={[styles.methodButtonText, digitalMethod === 'paypal' && styles.methodButtonTextActive]}>
              PayPal
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.methodButton, digitalMethod === 'nequi' && styles.methodButtonActive]}
            onPress={() => setDigitalMethod('nequi')}
          >
            <Text style={styles.methodButtonIcon}>📱</Text>
            <Text style={[styles.methodButtonText, digitalMethod === 'nequi' && styles.methodButtonTextActive]}>
              Nequi
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Formulario específico según método */}
      {digitalMethod === 'card' && (
        <View style={styles.cardForm}>
          <Text style={styles.fieldLabel}>Número de Tarjeta</Text>
          <TextInput
            style={styles.textInput}
            value={cardNumber}
            onChangeText={(text) => setCardNumber(formatCardNumber(text))}
            placeholder="1234 5678 9012 3456"
            keyboardType="numeric"
            maxLength={19}
          />
          
          <View style={styles.row}>
            <View style={styles.halfWidth}>
              <Text style={styles.fieldLabel}>Fecha de Expiración</Text>
              <TextInput
                style={styles.textInput}
                value={cardExpiry}
                onChangeText={(text) => setCardExpiry(formatExpiry(text))}
                placeholder="MM/YY"
                maxLength={5}
              />
            </View>
            <View style={styles.halfWidth}>
              <Text style={styles.fieldLabel}>CVV</Text>
              <TextInput
                style={styles.textInput}
                value={cardCvv}
                onChangeText={setCardCvv}
                placeholder="123"
                keyboardType="numeric"
                maxLength={4}
                secureTextEntry
              />
            </View>
          </View>
          
          <Text style={styles.fieldLabel}>Nombre del Titular</Text>
          <TextInput
            style={styles.textInput}
            value={cardholderName}
            onChangeText={setCardholderName}
            placeholder="Nombre completo"
            autoCapitalize="words"
          />
        </View>
      )}

      {digitalMethod === 'paypal' && (
        <View style={styles.paypalForm}>
          <Text style={styles.fieldLabel}>Email de PayPal</Text>
          <TextInput
            style={styles.textInput}
            value={paypalEmail}
            onChangeText={setPaypalEmail}
            placeholder="tu@email.com"
            keyboardType="email-address"
            autoCapitalize="none"
          />
          <Text style={styles.helpText}>
            Se te redirigirá a PayPal para completar el pago
          </Text>
        </View>
      )}

      {digitalMethod === 'nequi' && (
        <View style={styles.nequiForm}>
          <Text style={styles.fieldLabel}>Número de Teléfono</Text>
          <TextInput
            style={styles.textInput}
            value={nequiPhone}
            onChangeText={setNequiPhone}
            placeholder="300 123 4567"
            keyboardType="phone-pad"
          />
          <Text style={styles.helpText}>
            Recibirás un código de verificación por SMS
          </Text>
        </View>
      )}
    </View>
  );

  const renderCashPaymentForm = () => (
    <View style={styles.paymentForm}>
      <Text style={styles.sectionTitle}>Pago en Efectivo</Text>
      
      <Text style={styles.fieldLabel}>Número de Referencia</Text>
      <TextInput
        style={styles.textInput}
        value={referenceNumber}
        onChangeText={setReferenceNumber}
        placeholder="Número de recibo o referencia"
      />
      
      <Text style={styles.helpText}>
        Entrega el dinero al organizador y solicita un número de referencia
      </Text>
    </View>
  );

  const renderPaymentSummary = () => (
    <View style={styles.summaryCard}>
      <Text style={styles.summaryTitle}>Resumen del Pago</Text>
      
      <View style={styles.summaryRow}>
        <Text style={styles.summaryLabel}>Concepto:</Text>
        <Text style={styles.summaryValue}>{description}</Text>
      </View>
      
      <View style={styles.summaryRow}>
        <Text style={styles.summaryLabel}>Monto:</Text>
        <Text style={styles.summaryAmount}>${amount.toLocaleString()}</Text>
      </View>
      
      <View style={styles.summaryRow}>
        <Text style={styles.summaryLabel}>Método:</Text>
        <Text style={styles.summaryValue}>
          {paymentMethod === 'digital' 
            ? digitalMethod === 'card' ? 'Tarjeta de Crédito/Débito'
            : digitalMethod === 'paypal' ? 'PayPal'
            : 'Nequi'
            : 'Efectivo'
          }
        </Text>
      </View>
      
      {notes && (
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Notas:</Text>
          <Text style={styles.summaryValue}>{notes}</Text>
        </View>
      )}
    </View>
  );

  if (!user) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Debes iniciar sesión para realizar pagos</Text>
      </View>
    );
  }

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
        
        <Text style={styles.headerTitle}>Procesar Pago</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Resumen del pago */}
        {renderPaymentSummary()}

        {/* Selección de método de pago */}
        <View style={styles.methodSection}>
          <Text style={styles.sectionTitle}>Método de Pago</Text>
          <View style={styles.methodToggle}>
            <TouchableOpacity
              style={[styles.toggleButton, paymentMethod === 'digital' && styles.toggleButtonActive]}
              onPress={() => setPaymentMethod('digital')}
            >
              <Text style={[styles.toggleButtonText, paymentMethod === 'digital' && styles.toggleButtonTextActive]}>
                💳 Digital
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.toggleButton, paymentMethod === 'cash' && styles.toggleButtonActive]}
              onPress={() => setPaymentMethod('cash')}
            >
              <Text style={[styles.toggleButtonText, paymentMethod === 'cash' && styles.toggleButtonTextActive]}>
                💰 Efectivo
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Formulario de pago */}
        {paymentMethod === 'digital' ? renderDigitalPaymentForm() : renderCashPaymentForm()}

        {/* Notas adicionales */}
        <View style={styles.notesSection}>
          <Text style={styles.fieldLabel}>Notas Adicionales (Opcional)</Text>
          <TextInput
            style={[styles.textInput, styles.notesInput]}
            value={notes}
            onChangeText={setNotes}
            placeholder="Información adicional sobre el pago..."
            multiline
            numberOfLines={3}
            textAlignVertical="top"
          />
        </View>

        {/* Botón de pago */}
        <TouchableOpacity
          style={[styles.payButton, processing && styles.payButtonDisabled]}
          onPress={handlePayment}
          disabled={processing}
        >
          <Text style={styles.payButtonText}>
            {processing ? 'Procesando...' : `Pagar $${amount.toLocaleString()}`}
          </Text>
        </TouchableOpacity>

        <View style={styles.disclaimer}>
          <Text style={styles.disclaimerText}>
            💡 Este es un pago simulado para fines de demostración. No se realizarán cargos reales.
          </Text>
        </View>
      </ScrollView>

      {/* Modal de éxito */}
      <Modal
        visible={showSuccessModal}
        transparent={true}
        animationType="fade"
        onRequestClose={handleSuccessClose}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.successModal}>
            <View style={styles.successIcon}>✅</View>
            <Text style={styles.successTitle}>¡Pago Exitoso!</Text>
            <Text style={styles.successMessage}>
              Tu pago ha sido procesado correctamente
            </Text>
            
            {paymentResult && (
              <View style={styles.paymentDetails}>
                <Text style={styles.detailLabel}>Referencia:</Text>
                <Text style={styles.detailValue}>{paymentResult.referencia}</Text>
                
                <Text style={styles.detailLabel}>Estado:</Text>
                <Text style={styles.detailValue}>
                  {paymentResult.estado === 'pendiente' ? '⏳ Pendiente' : '✅ Confirmado'}
                </Text>
                
                <Text style={styles.detailLabel}>Fecha:</Text>
                <Text style={styles.detailValue}>
                  {new Date(paymentResult.fecha_creacion).toLocaleDateString('es-CO')}
                </Text>
              </View>
            )}
            
            <TouchableOpacity
              style={styles.successButton}
              onPress={handleSuccessClose}
            >
              <Text style={styles.successButtonText}>Continuar</Text>
            </TouchableOpacity>
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
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1E293B',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#64748B',
  },
  summaryValue: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '500',
    textAlign: 'right',
    flex: 1,
  },
  summaryAmount: {
    fontSize: 18,
    color: '#10B981',
    fontWeight: 'bold',
  },
  methodSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 16,
  },
  methodToggle: {
    flexDirection: 'row',
    backgroundColor: '#F1F5F9',
    borderRadius: 12,
    padding: 4,
  },
  toggleButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  toggleButtonActive: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  toggleButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#64748B',
  },
  toggleButtonTextActive: {
    color: '#1E293B',
  },
  paymentForm: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  methodSelector: {
    marginBottom: 20,
  },
  methodButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  methodButton: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  methodButtonActive: {
    backgroundColor: '#EFF6FF',
    borderColor: '#3B82F6',
  },
  methodButtonIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  methodButtonText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#64748B',
  },
  methodButtonTextActive: {
    color: '#3B82F6',
  },
  cardForm: {
    gap: 16,
  },
  paypalForm: {
    gap: 16,
  },
  nequiForm: {
    gap: 16,
  },
  fieldLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
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
  notesInput: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    gap: 16,
  },
  halfWidth: {
    flex: 1,
  },
  helpText: {
    fontSize: 12,
    color: '#94A3B8',
    fontStyle: 'italic',
    marginTop: 4,
  },
  notesSection: {
    marginBottom: 24,
  },
  payButton: {
    backgroundColor: '#10B981',
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: 'center',
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  payButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  payButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  disclaimer: {
    backgroundColor: '#FEF3C7',
    borderRadius: 8,
    padding: 16,
    marginBottom: 20,
  },
  disclaimerText: {
    fontSize: 12,
    color: '#92400E',
    textAlign: 'center',
    lineHeight: 18,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  successModal: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 32,
    margin: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 10,
    },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 10,
  },
  successIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#10B981',
    marginBottom: 8,
  },
  successMessage: {
    fontSize: 16,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 24,
  },
  paymentDetails: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    width: '100%',
  },
  detailLabel: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 14,
    color: '#1E293B',
    fontWeight: '600',
    marginBottom: 12,
  },
  successButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 32,
    width: '100%',
    alignItems: 'center',
  },
  successButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default PaymentScreen;
