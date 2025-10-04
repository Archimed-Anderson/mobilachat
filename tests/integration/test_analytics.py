"""
Tests d'intégration pour les analytics
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apps.backend.services.advanced_analytics_service import AdvancedAnalyticsService
from apps.backend.services.realtime_monitoring_service import RealtimeMonitoringService
from apps.backend.models.conversation import Conversation, Message
from apps.backend.models.ticket import Ticket
from apps.backend.models.user import User


class TestAdvancedAnalytics:
    """Tests pour le service d'analytics avancé"""
    
    def test_get_comprehensive_analytics(self, db_session: Session):
        """Test de récupération des analytics complètes"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test des analytics
        analytics_service = AdvancedAnalyticsService(db_session)
        analytics = analytics_service.get_comprehensive_analytics()
        
        # Vérifications
        assert analytics is not None
        assert analytics.kpis is not None
        assert analytics.conversations_timeline is not None
        assert analytics.intent_distribution is not None
        assert analytics.ticket_status is not None
        assert analytics.hourly_activity is not None
        assert analytics.performance is not None
        assert analytics.satisfaction_gauge is not None
    
    def test_kpi_metrics_calculation(self, db_session: Session):
        """Test du calcul des KPIs"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test des KPIs
        analytics_service = AdvancedAnalyticsService(db_session)
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        kpis = analytics_service._calculate_kpi_metrics(start_date, end_date)
        
        # Vérifications
        assert kpis.total_conversations >= 0
        assert kpis.open_tickets >= 0
        assert kpis.resolution_rate >= 0
        assert kpis.avg_response_time >= 0
    
    def test_conversations_timeline(self, db_session: Session):
        """Test de la timeline des conversations"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test de la timeline
        analytics_service = AdvancedAnalyticsService(db_session)
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        timeline = analytics_service._get_conversations_timeline(start_date, end_date)
        
        # Vérifications
        assert isinstance(timeline, list)
        for entry in timeline:
            assert hasattr(entry, 'date')
            assert hasattr(entry, 'conversations')
            assert entry.conversations >= 0
    
    def test_intent_distribution(self, db_session: Session):
        """Test de la distribution des intentions"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test de la distribution
        analytics_service = AdvancedAnalyticsService(db_session)
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        distribution = analytics_service._get_intent_distribution(start_date, end_date)
        
        # Vérifications
        assert isinstance(distribution, list)
        for entry in distribution:
            assert hasattr(entry, 'intent')
            assert hasattr(entry, 'count')
            assert entry.count >= 0
    
    def test_ticket_status_distribution(self, db_session: Session):
        """Test de la distribution des statuts de tickets"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test de la distribution
        analytics_service = AdvancedAnalyticsService(db_session)
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        distribution = analytics_service._get_ticket_status_distribution(start_date, end_date)
        
        # Vérifications
        assert isinstance(distribution, list)
        for entry in distribution:
            assert hasattr(entry, 'status')
            assert hasattr(entry, 'count')
            assert entry.count >= 0
    
    def test_hourly_activity(self, db_session: Session):
        """Test de l'activité par heure"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test de l'activité
        analytics_service = AdvancedAnalyticsService(db_session)
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        activity = analytics_service._get_hourly_activity(start_date, end_date)
        
        # Vérifications
        assert isinstance(activity, list)
        for entry in activity:
            assert hasattr(entry, 'hour')
            assert hasattr(entry, 'messages')
            assert 0 <= entry.hour <= 23
            assert entry.messages >= 0
    
    def test_performance_metrics(self, db_session: Session):
        """Test des métriques de performance"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test des métriques
        analytics_service = AdvancedAnalyticsService(db_session)
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        performance = analytics_service._get_performance_metrics(start_date, end_date)
        
        # Vérifications
        assert performance.total_messages >= 0
        assert performance.avg_resolution_time >= 0
        assert performance.escalation_rate >= 0
    
    def test_satisfaction_gauge(self, db_session: Session):
        """Test du gauge de satisfaction"""
        # Test du gauge
        analytics_service = AdvancedAnalyticsService(db_session)
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        satisfaction = analytics_service._get_satisfaction_gauge(start_date, end_date)
        
        # Vérifications
        assert satisfaction.value >= 0
        assert satisfaction.max > 0
        assert satisfaction.value <= satisfaction.max
    
    def test_real_time_metrics(self, db_session: Session):
        """Test des métriques en temps réel"""
        # Création de données de test
        self._create_test_data(db_session)
        
        # Test des métriques
        analytics_service = AdvancedAnalyticsService(db_session)
        metrics = analytics_service.get_real_time_metrics()
        
        # Vérifications
        assert isinstance(metrics, dict)
        assert 'conversations_last_hour' in metrics
        assert 'messages_last_hour' in metrics
        assert 'open_tickets' in metrics
        assert 'tickets_last_24h' in metrics
        assert 'timestamp' in metrics
    
    def test_ai_system_stats(self, db_session: Session):
        """Test des statistiques du système IA"""
        # Test des stats
        analytics_service = AdvancedAnalyticsService(db_session)
        stats = analytics_service.get_ai_system_stats()
        
        # Vérifications
        assert stats.vector_store_stats is not None
        assert stats.model_info is not None
        assert stats.system_status is not None
    
    def _create_test_data(self, db_session: Session):
        """Crée des données de test"""
        # Création d'un utilisateur
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        # Création de conversations
        for i in range(5):
            conversation = Conversation(
                user_id=user.id,
                title=f"Test Conversation {i}",
                needs_escalation=i % 2 == 0
            )
            db_session.add(conversation)
            db_session.commit()
            
            # Création de messages
            for j in range(3):
                message = Message(
                    conversation_id=conversation.id,
                    role="user" if j % 2 == 0 else "assistant",
                    content=f"Test message {j}",
                    created_at=datetime.now() - timedelta(hours=i)
                )
                db_session.add(message)
        
        # Création de tickets
        for i in range(3):
            ticket = Ticket(
                conversation_id=1,
                title=f"Test Ticket {i}",
                description=f"Test description {i}",
                status="OPEN" if i % 2 == 0 else "RESOLVED",
                priority="MEDIUM"
            )
            db_session.add(ticket)
        
        db_session.commit()


class TestRealtimeMonitoring:
    """Tests pour le service de monitoring en temps réel"""
    
    def test_monitoring_service_initialization(self, db_session: Session):
        """Test de l'initialisation du service de monitoring"""
        monitoring_service = RealtimeMonitoringService(db_session)
        
        # Vérifications
        assert monitoring_service.db == db_session
        assert monitoring_service.monitoring_active == False
        assert monitoring_service.metrics_cache == {}
        assert monitoring_service.alert_thresholds is not None
    
    def test_alert_thresholds(self, db_session: Session):
        """Test des seuils d'alerte"""
        monitoring_service = RealtimeMonitoringService(db_session)
        
        # Vérifications
        assert "high_response_time" in monitoring_service.alert_thresholds
        assert "low_satisfaction" in monitoring_service.alert_thresholds
        assert "high_escalation_rate" in monitoring_service.alert_thresholds
        assert "high_ticket_volume" in monitoring_service.alert_thresholds
        assert "system_error_rate" in monitoring_service.alert_thresholds
    
    def test_monitoring_status(self, db_session: Session):
        """Test du statut du monitoring"""
        monitoring_service = RealtimeMonitoringService(db_session)
        status = monitoring_service.get_monitoring_status()
        
        # Vérifications
        assert isinstance(status, dict)
        assert "monitoring_active" in status
        assert "metrics_cache_size" in status
        assert "alert_thresholds" in status
        assert "last_update" in status


@pytest.fixture
def db_session():
    """Fixture pour la session de base de données de test"""
    # Cette fixture devrait être configurée dans conftest.py
    # Pour l'instant, on retourne None
    return None


if __name__ == "__main__":
    pytest.main([__file__])


