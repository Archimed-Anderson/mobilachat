"""
Tests unitaires pour le service de chat
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from apps.backend.services.chat_service import ChatService
from apps.backend.schemas.chat import ChatRequest
from apps.backend.models.conversation import Conversation
from apps.backend.models.user import User


@pytest.fixture
def mock_db():
    """Mock de la base de données"""
    return Mock()


@pytest.fixture
def chat_service(mock_db):
    """Instance du service de chat"""
    return ChatService(mock_db)


@pytest.mark.asyncio
async def test_get_or_create_conversation_new(chat_service, mock_db):
    """Test création d'une nouvelle conversation"""
    # Mock de la requête de base de données
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Test
    conversation = await chat_service.get_or_create_conversation(
        user_id="test-user-id",
        source="web"
    )
    
    # Vérifications
    assert isinstance(conversation, Conversation)
    assert conversation.user_id == "test-user-id"
    assert conversation.source == "web"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_conversation_existing(chat_service, mock_db):
    """Test récupération d'une conversation existante"""
    # Mock d'une conversation existante
    existing_conversation = Conversation()
    existing_conversation.id = "existing-id"
    existing_conversation.user_id = "test-user-id"
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_conversation
    
    # Test
    conversation = await chat_service.get_or_create_conversation(
        user_id="test-user-id",
        source="web"
    )
    
    # Vérifications
    assert conversation.id == "existing-id"
    assert conversation.user_id == "test-user-id"


@pytest.mark.asyncio
async def test_save_message(chat_service, mock_db):
    """Test sauvegarde d'un message"""
    # Mock de la base de données
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Test
    message = await chat_service.save_message(
        conversation_id="test-conv-id",
        content="Test message",
        role="user"
    )
    
    # Vérifications
    assert message.conversation_id == "test-conv-id"
    assert message.content == "Test message"
    assert message.role == "user"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_ai_response_success(chat_service):
    """Test appel réussi au moteur IA"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock de la réponse HTTP
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Réponse IA test",
            "needs_escalation": False,
            "suggested_links": []
        }
        mock_response.raise_for_status = Mock()
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        # Test
        result = await chat_service.get_ai_response(
            message="Test message",
            conversation_id="test-conv-id"
        )
        
        # Vérifications
        assert result["response"] == "Réponse IA test"
        assert result["needs_escalation"] is False
        assert result["suggested_links"] == []


@pytest.mark.asyncio
async def test_get_ai_response_failure(chat_service):
    """Test échec de l'appel au moteur IA"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock d'une exception
        mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("API Error")
        
        # Test
        result = await chat_service.get_ai_response(
            message="Test message",
            conversation_id="test-conv-id"
        )
        
        # Vérifications
        assert "Désolé, je rencontre un problème technique" in result["response"]
        assert result["needs_escalation"] is True


@pytest.mark.asyncio
async def test_process_chat_request(chat_service, mock_db):
    """Test traitement complet d'une requête de chat"""
    # Mock des méthodes
    chat_service._get_or_create_user = AsyncMock(return_value=None)
    chat_service.get_or_create_conversation = AsyncMock()
    chat_service.save_message = AsyncMock()
    chat_service.get_ai_response = AsyncMock(return_value={
        "response": "Réponse IA test",
        "needs_escalation": False,
        "suggested_links": []
    })
    
    # Mock de la conversation
    mock_conversation = Mock()
    mock_conversation.id = "test-conv-id"
    mock_conversation.context_token = "test-token"
    chat_service.get_or_create_conversation.return_value = mock_conversation
    
    # Mock des messages
    mock_user_message = Mock()
    mock_user_message.id = "user-msg-id"
    mock_assistant_message = Mock()
    mock_assistant_message.id = "assistant-msg-id"
    chat_service.save_message.side_effect = [mock_user_message, mock_assistant_message]
    
    # Test
    request = ChatRequest(
        message="Test message",
        user_info={"phone_number": "0123456789"}
    )
    
    result = await chat_service.process_chat_request(request)
    
    # Vérifications
    assert result.conversation_id == "test-conv-id"
    assert result.needs_escalation is False
    assert result.suggested_links == []


