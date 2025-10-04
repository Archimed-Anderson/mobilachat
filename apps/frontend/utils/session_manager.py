"""
Gestionnaire de session Streamlit
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import uuid
import json


class SessionManager:
    def __init__(self):
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialise les variables de session"""
        if "initialized" not in st.session_state:
            st.session_state.initialized = True
            st.session_state.user_info = {}
            st.session_state.conversation_id = None
            st.session_state.messages = []
            st.session_state.context_token = None
            st.session_state.last_activity = datetime.now()
            st.session_state.escalation_warning = False
            st.session_state.suggested_links = []
            st.session_state.typing = False
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.session_timeout = 3600  # 1 heure
    
    def is_session_valid(self) -> bool:
        """Vérifie si la session est encore valide"""
        if "last_activity" not in st.session_state:
            return False
        
        timeout = timedelta(seconds=st.session_state.session_timeout)
        return datetime.now() - st.session_state.last_activity < timeout
    
    def update_activity(self):
        """Met à jour la dernière activité"""
        st.session_state.last_activity = datetime.now()
    
    def reset_session(self):
        """Remet à zéro la session"""
        st.session_state.user_info = {}
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.context_token = None
        st.session_state.last_activity = datetime.now()
        st.session_state.escalation_warning = False
        st.session_state.suggested_links = []
        st.session_state.typing = False
        st.session_state.authenticated = False
        st.session_state.user_id = None
    
    def set_user_info(self, user_info: Dict[str, Any]):
        """Définit les informations utilisateur"""
        st.session_state.user_info = user_info
        st.session_state.authenticated = True
        self.update_activity()
    
    def get_user_info(self) -> Dict[str, Any]:
        """Récupère les informations utilisateur"""
        return st.session_state.get("user_info", {})
    
    def set_conversation_id(self, conversation_id: str):
        """Définit l'ID de conversation"""
        st.session_state.conversation_id = conversation_id
        self.update_activity()
    
    def get_conversation_id(self) -> Optional[str]:
        """Récupère l'ID de conversation"""
        return st.session_state.get("conversation_id")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Ajoute un message à la conversation"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        st.session_state.messages.append(message)
        
        # Limitation du nombre de messages
        max_messages = 100
        if len(st.session_state.messages) > max_messages:
            st.session_state.messages = st.session_state.messages[-max_messages:]
        
        self.update_activity()
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Récupère tous les messages"""
        return st.session_state.get("messages", [])
    
    def clear_messages(self):
        """Efface tous les messages"""
        st.session_state.messages = []
        self.update_activity()
    
    def set_context_token(self, token: str):
        """Définit le token de contexte"""
        st.session_state.context_token = token
        self.update_activity()
    
    def get_context_token(self) -> Optional[str]:
        """Récupère le token de contexte"""
        return st.session_state.get("context_token")
    
    def set_escalation_warning(self, warning: bool):
        """Définit l'avertissement d'escalade"""
        st.session_state.escalation_warning = warning
        self.update_activity()
    
    def get_escalation_warning(self) -> bool:
        """Récupère l'avertissement d'escalade"""
        return st.session_state.get("escalation_warning", False)
    
    def set_suggested_links(self, links: List[Dict[str, str]]):
        """Définit les liens suggérés"""
        st.session_state.suggested_links = links
        self.update_activity()
    
    def get_suggested_links(self) -> List[Dict[str, str]]:
        """Récupère les liens suggérés"""
        return st.session_state.get("suggested_links", [])
    
    def set_typing(self, typing: bool):
        """Définit l'état de frappe"""
        st.session_state.typing = typing
    
    def get_typing(self) -> bool:
        """Récupère l'état de frappe"""
        return st.session_state.get("typing", False)
    
    def generate_context_token(self) -> str:
        """Génère un nouveau token de contexte"""
        token = str(uuid.uuid4())
        self.set_context_token(token)
        return token
    
    def get_session_data(self) -> Dict[str, Any]:
        """Récupère toutes les données de session"""
        return {
            "user_info": self.get_user_info(),
            "conversation_id": self.get_conversation_id(),
            "messages": self.get_messages(),
            "context_token": self.get_context_token(),
            "escalation_warning": self.get_escalation_warning(),
            "suggested_links": self.get_suggested_links(),
            "typing": self.get_typing(),
            "authenticated": st.session_state.get("authenticated", False),
            "last_activity": st.session_state.get("last_activity", datetime.now()).isoformat()
        }
    
    def load_session_data(self, data: Dict[str, Any]):
        """Charge les données de session"""
        if "user_info" in data:
            st.session_state.user_info = data["user_info"]
        if "conversation_id" in data:
            st.session_state.conversation_id = data["conversation_id"]
        if "messages" in data:
            st.session_state.messages = data["messages"]
        if "context_token" in data:
            st.session_state.context_token = data["context_token"]
        if "escalation_warning" in data:
            st.session_state.escalation_warning = data["escalation_warning"]
        if "suggested_links" in data:
            st.session_state.suggested_links = data["suggested_links"]
        if "typing" in data:
            st.session_state.typing = data["typing"]
        if "authenticated" in data:
            st.session_state.authenticated = data["authenticated"]
        if "last_activity" in data:
            st.session_state.last_activity = datetime.fromisoformat(data["last_activity"])
        
        self.update_activity()


# Instance globale
session_manager = SessionManager()


