"""
Tests unitaires pour le service de tickets
"""
import pytest
from unittest.mock import Mock, AsyncMock
from apps.backend.services.ticket_service import TicketService
from apps.backend.schemas.ticket import TicketCreate, TicketUpdate
from apps.backend.models.ticket import Ticket


@pytest.fixture
def mock_db():
    """Mock de la base de données"""
    return Mock()


@pytest.fixture
def ticket_service(mock_db):
    """Instance du service de tickets"""
    return TicketService(mock_db)


@pytest.mark.asyncio
async def test_create_ticket(ticket_service, mock_db):
    """Test création d'un ticket"""
    # Mock de la base de données
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Test
    ticket_data = TicketCreate(
        conversation_id="test-conv-id",
        priority="HIGH",
        category="technique"
    )
    
    ticket = await ticket_service.create_ticket(ticket_data)
    
    # Vérifications
    assert isinstance(ticket, Ticket)
    assert ticket.conversation_id == "test-conv-id"
    assert ticket.priority == "HIGH"
    assert ticket.category == "technique"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_ticket_existing(ticket_service, mock_db):
    """Test récupération d'un ticket existant"""
    # Mock d'un ticket existant
    existing_ticket = Ticket()
    existing_ticket.id = "test-ticket-id"
    existing_ticket.priority = "MEDIUM"
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_ticket
    
    # Test
    ticket = await ticket_service.get_ticket("test-ticket-id")
    
    # Vérifications
    assert ticket.id == "test-ticket-id"
    assert ticket.priority == "MEDIUM"


@pytest.mark.asyncio
async def test_get_ticket_not_found(ticket_service, mock_db):
    """Test récupération d'un ticket inexistant"""
    # Mock d'aucun ticket trouvé
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Test
    ticket = await ticket_service.get_ticket("non-existent-id")
    
    # Vérifications
    assert ticket is None


@pytest.mark.asyncio
async def test_update_ticket(ticket_service, mock_db):
    """Test mise à jour d'un ticket"""
    # Mock d'un ticket existant
    existing_ticket = Mock()
    existing_ticket.id = "test-ticket-id"
    existing_ticket.priority = "MEDIUM"
    existing_ticket.status = "OPEN"
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_ticket
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Test
    update_data = TicketUpdate(
        priority="HIGH",
        status="IN_PROGRESS"
    )
    
    ticket = await ticket_service.update_ticket("test-ticket-id", update_data)
    
    # Vérifications
    assert ticket.priority == "HIGH"
    assert ticket.status == "IN_PROGRESS"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_assign_ticket(ticket_service, mock_db):
    """Test assignation d'un ticket"""
    # Mock d'un ticket existant
    existing_ticket = Mock()
    existing_ticket.id = "test-ticket-id"
    existing_ticket.assigned_to = None
    existing_ticket.status = "OPEN"
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_ticket
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Test
    ticket = await ticket_service.assign_ticket("test-ticket-id", "user-id")
    
    # Vérifications
    assert ticket.assigned_to == "user-id"
    assert ticket.status == "IN_PROGRESS"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_resolve_ticket(ticket_service, mock_db):
    """Test résolution d'un ticket"""
    # Mock d'un ticket existant
    existing_ticket = Mock()
    existing_ticket.id = "test-ticket-id"
    existing_ticket.status = "IN_PROGRESS"
    existing_ticket.resolution_notes = None
    existing_ticket.assigned_to = None
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_ticket
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Test
    ticket = await ticket_service.resolve_ticket(
        "test-ticket-id", 
        "Problème résolu", 
        "user-id"
    )
    
    # Vérifications
    assert ticket.status == "RESOLVED"
    assert ticket.resolution_notes == "Problème résolu"
    assert ticket.assigned_to == "user-id"
    mock_db.commit.assert_called_once()


