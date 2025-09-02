import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  RefreshControl,
  Modal,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../types';
import { Comment, CommentForm } from '../types';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

type CommentsScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Comments'>;
type CommentsScreenRouteProp = RouteProp<RootStackParamList, 'Comments'>;

const CommentsScreen: React.FC = () => {
  const navigation = useNavigation<CommentsScreenNavigationProp>();
  const route = useRoute<CommentsScreenRouteProp>();
  const { user } = useAuth();
  
  const { contentId, contentType } = route.params;
  
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [addingComment, setAddingComment] = useState(false);
  const [replyingTo, setReplyingTo] = useState<Comment | null>(null);
  const [replyText, setReplyText] = useState('');
  const [addingReply, setAddingReply] = useState(false);

  useEffect(() => {
    loadComments();
  }, [contentId, contentType]);

  const loadComments = async () => {
    try {
      setLoading(true);
      const response = await apiService.getComments(contentType, contentId);
      
      if (response.success && response.data) {
        setComments(response.data);
      } else {
        console.error('Error loading comments:', response.message);
      }
    } catch (error) {
      console.error('Error loading comments:', error);
      Alert.alert('Error', 'No se pudieron cargar los comentarios');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadComments();
    setRefreshing(false);
  };

  const handleAddComment = async () => {
    if (!user) {
      Alert.alert('Error', 'Debes iniciar sesión para comentar');
      return;
    }

    if (!newComment.trim()) {
      Alert.alert('Error', 'El comentario no puede estar vacío');
      return;
    }

    try {
      setAddingComment(true);
      const commentData: CommentForm = {
        texto: newComment.trim(),
      };

      const response = await apiService.addComment(contentType, contentId, commentData);
      
      if (response.success && response.data) {
        setComments(prev => [response.data!, ...prev]);
        setNewComment('');
        setShowAddModal(false);
        Alert.alert('Éxito', 'Comentario agregado correctamente');
      } else {
        Alert.alert('Error', response.message || 'No se pudo agregar el comentario');
      }
    } catch (error) {
      console.error('Error adding comment:', error);
      Alert.alert('Error', 'No se pudo agregar el comentario');
    } finally {
      setAddingComment(false);
    }
  };

  const handleAddReply = async () => {
    if (!user || !replyingTo) {
      return;
    }

    if (!replyText.trim()) {
      Alert.alert('Error', 'La respuesta no puede estar vacía');
      return;
    }

    try {
      setAddingReply(true);
      const commentData: CommentForm = {
        texto: replyText.trim(),
        comentario_padre: replyingTo.id,
      };

      const response = await apiService.addComment(contentType, contentId, commentData);
      
      if (response.success && response.data) {
        // Agregar la respuesta al comentario padre
        setComments(prev => 
          prev.map(comment => 
            comment.id === replyingTo.id 
              ? { ...comment, respuestas: [...comment.respuestas, response.data!] }
              : comment
          )
        );
        setReplyText('');
        setReplyingTo(null);
        Alert.alert('Éxito', 'Respuesta agregada correctamente');
      } else {
        Alert.alert('Error', response.message || 'No se pudo agregar la respuesta');
      }
    } catch (error) {
      console.error('Error adding reply:', error);
      Alert.alert('Error', 'No se pudo agregar la respuesta');
    } finally {
      setAddingReply(false);
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    Alert.alert(
      'Eliminar Comentario',
      '¿Estás seguro de que quieres eliminar este comentario?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Eliminar', 
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await apiService.deleteComment(commentId);
              
              if (response.success) {
                setComments(prev => prev.filter(comment => comment.id !== commentId));
                Alert.alert('Éxito', 'Comentario eliminado correctamente');
              } else {
                Alert.alert('Error', response.message || 'No se pudo eliminar el comentario');
              }
            } catch (error) {
              console.error('Error deleting comment:', error);
              Alert.alert('Error', 'No se pudo eliminar el comentario');
            }
          }
        },
      ]
    );
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

  const getContentTypeTitle = () => {
    switch (contentType) {
      case 'san':
        return 'SAN';
      case 'rifa':
        return 'Rifa';
      default:
        return 'Contenido';
    }
  };

  const renderComment = (comment: Comment, isReply: boolean = false) => (
    <View key={comment.id} style={[styles.commentCard, isReply && styles.replyCard]}>
      <View style={styles.commentHeader}>
        <View style={styles.commentUserInfo}>
          <View style={styles.userAvatar}>
            <Text style={styles.userAvatarText}>
              {comment.usuario.username[0].toUpperCase()}
            </Text>
          </View>
          <View style={styles.commentMeta}>
            <Text style={styles.commentUsername}>{comment.usuario.username}</Text>
            <Text style={styles.commentDate}>{formatDate(comment.fecha_creacion)}</Text>
          </View>
        </View>
        
        {user && (user.id === comment.usuario.id || user.is_staff) && (
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={() => handleDeleteComment(comment.id)}
          >
            <Text style={styles.deleteButtonText}>🗑️</Text>
          </TouchableOpacity>
        )}
      </View>

      <Text style={styles.commentText}>{comment.texto}</Text>

      <View style={styles.commentActions}>
        <View style={styles.votesContainer}>
          <TouchableOpacity style={styles.voteButton}>
            <Text style={styles.voteButtonText}>👍 {comment.votos_positivos}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.voteButton}>
            <Text style={styles.voteButtonText}>👎 {comment.votos_negativos}</Text>
          </TouchableOpacity>
        </View>

        {!isReply && (
          <TouchableOpacity
            style={styles.replyButton}
            onPress={() => setReplyingTo(comment)}
          >
            <Text style={styles.replyButtonText}>Responder</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Respuestas */}
      {comment.respuestas && comment.respuestas.length > 0 && (
        <View style={styles.repliesContainer}>
          {comment.respuestas.map((reply) => renderComment(reply, true))}
        </View>
      )}
    </View>
  );

  if (!user) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Debes iniciar sesión para ver comentarios</Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Cargando comentarios...</Text>
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
        
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>Comentarios del {getContentTypeTitle()}</Text>
          <TouchableOpacity
            style={styles.addCommentButton}
            onPress={() => setShowAddModal(true)}
          >
            <Text style={styles.addCommentButtonText}>+ Comentar</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Comments List */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {comments.length > 0 ? (
          <View style={styles.commentsContainer}>
            {comments.map(renderComment)}
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateIcon}>💬</Text>
            <Text style={styles.emptyStateText}>No hay comentarios aún</Text>
            <Text style={styles.emptyStateSubtext}>
              Sé el primero en comentar sobre este {getContentTypeTitle().toLowerCase()}
            </Text>
            <TouchableOpacity
              style={styles.addFirstCommentButton}
              onPress={() => setShowAddModal(true)}
            >
              <Text style={styles.addFirstCommentButtonText}>Agregar primer comentario</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      {/* Add Comment Modal */}
      <Modal
        visible={showAddModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowAddModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Agregar Comentario</Text>
            
            <TextInput
              style={styles.commentInput}
              value={newComment}
              onChangeText={setNewComment}
              placeholder="Escribe tu comentario..."
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => {
                  setShowAddModal(false);
                  setNewComment('');
                }}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.confirmButton, (!newComment.trim() || addingComment) && styles.confirmButtonDisabled]}
                onPress={handleAddComment}
                disabled={!newComment.trim() || addingComment}
              >
                <Text style={styles.confirmButtonText}>
                  {addingComment ? 'Agregando...' : 'Agregar'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Reply Modal */}
      <Modal
        visible={!!replyingTo}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setReplyingTo(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Responder Comentario</Text>
            
            {replyingTo && (
              <View style={styles.replyToContainer}>
                <Text style={styles.replyToLabel}>Respondiendo a:</Text>
                <Text style={styles.replyToText}>{replyingTo.usuario.username}</Text>
                <Text style={styles.replyToComment}>{replyingTo.texto}</Text>
              </View>
            )}
            
            <TextInput
              style={styles.commentInput}
              value={replyText}
              onChangeText={setReplyText}
              placeholder="Escribe tu respuesta..."
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => {
                  setReplyingTo(null);
                  setReplyText('');
                }}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.confirmButton, (!replyText.trim() || addingReply) && styles.confirmButtonDisabled]}
                onPress={handleAddReply}
                disabled={!replyText.trim() || addingReply}
              >
                <Text style={styles.confirmButtonText}>
                  {addingReply ? 'Respondiendo...' : 'Responder'}
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
  headerTitle: {
    fontSize: 20,
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
  content: {
    flex: 1,
  },
  commentsContainer: {
    padding: 16,
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
  replyCard: {
    marginLeft: 32,
    marginTop: 12,
    backgroundColor: '#F8FAFC',
    borderLeftWidth: 3,
    borderLeftColor: '#E2E8F0',
  },
  commentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  commentUserInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  userAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  userAvatarText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  commentMeta: {
    flex: 1,
  },
  commentUsername: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 2,
  },
  commentDate: {
    fontSize: 12,
    color: '#94A3B8',
  },
  deleteButton: {
    padding: 4,
  },
  deleteButtonText: {
    fontSize: 16,
  },
  commentText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginBottom: 12,
  },
  commentActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  votesContainer: {
    flexDirection: 'row',
    gap: 16,
  },
  voteButton: {
    paddingVertical: 4,
    paddingHorizontal: 8,
  },
  voteButtonText: {
    fontSize: 12,
    color: '#64748B',
  },
  replyButton: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  replyButtonText: {
    fontSize: 12,
    color: '#3B82F6',
    fontWeight: '500',
  },
  repliesContainer: {
    marginTop: 12,
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
    marginBottom: 24,
  },
  addFirstCommentButton: {
    backgroundColor: '#3B82F6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  addFirstCommentButtonText: {
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
  replyToContainer: {
    backgroundColor: '#F8FAFC',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
    borderLeftWidth: 3,
    borderLeftColor: '#3B82F6',
  },
  replyToLabel: {
    fontSize: 12,
    color: '#64748B',
    marginBottom: 4,
  },
  replyToText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 8,
  },
  replyToComment: {
    fontSize: 14,
    color: '#64748B',
    fontStyle: 'italic',
  },
  commentInput: {
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#FFFFFF',
    minHeight: 100,
    marginBottom: 24,
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

export default CommentsScreen;
