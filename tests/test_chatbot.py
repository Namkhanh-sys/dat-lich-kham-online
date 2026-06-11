import pytest
from unittest.mock import MagicMock, patch
from src.gemini_chatbot import GeminiChatbot, SYSTEM_PROMPT, GREETING, chatbot_instance
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_chatbot_is_available():
    chatbot = GeminiChatbot()
    # If API key is not configured, it should return False
    with patch('config.Config.GEMINI_API_KEY', 'PASTE_YOUR_KEY_HERE'), \
         patch('config.Config.GROQ_API_KEY', 'PASTE_YOUR_KEY_HERE'):
        assert chatbot.is_available is False
    with patch('config.Config.GEMINI_API_KEY', 'valid_key_here'), \
         patch('config.Config.GROQ_API_KEY', 'PASTE_YOUR_KEY_HERE'):
        # Ensure _available is True or stubbed
        chatbot._available = True
        assert chatbot.is_available is True

@patch('google.genai.Client')
def test_chatbot_chat_flow(mock_client_class):
    # Setup mock client behavior
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = "Bạn cần đi khám Tai Mũi Họng. DOCTOR_SUGGESTION:{\"specialty\":\"Tai Mũi Họng\",\"keywords\":\"ho;đau họng\",\"advice\":\"Hãy đi khám sớm.\"}"
    mock_client.models.generate_content.return_value = mock_response

    # Force reset and mock Client initialization
    chatbot = GeminiChatbot()
    chatbot.client = mock_client
    chatbot._available = True
    chatbot.chat_sessions = {}

    with patch('config.Config.GEMINI_API_KEY', 'valid_key_here'), \
         patch('config.Config.GROQ_API_KEY', 'PASTE_YOUR_KEY_HERE'):
        result = chatbot.chat("session_123", "Tôi bị ho và đau họng")
        
        # Verify the structure of the reply
        assert "Tai Mũi Họng" in result["reply"]
        assert result["advice"] == "Hãy đi khám sớm."
        assert len(result["doctors"]) > 0
        assert result["doctors"][0]["id"] == "d1"  # "Tai Mũi Họng" is doctor d1 in conftest.py

def test_chatbot_page(client):
    response = client.get('/chatbot')
    assert response.status_code == 302
    assert response.location == '/'

@patch('src.gemini_chatbot.chatbot_instance.chat')
def test_api_chat(mock_chat, client):
    mock_chat.return_value = {
        "reply": "Mock reply",
        "doctors": [{"id": "d1", "name": "Bác sĩ X", "specialty": "Tai Mũi Họng"}],
        "advice": "Lời khuyên"
    }

    with patch('config.Config.GEMINI_API_KEY', 'valid_key_here'):
        chatbot_instance._available = True
        response = client.post('/api/chat', json={"message": "Tôi bị ho"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["reply"] == "Mock reply"
        assert len(data["doctors"]) == 1
        assert data["doctors"][0]["name"] == "Bác sĩ X"
