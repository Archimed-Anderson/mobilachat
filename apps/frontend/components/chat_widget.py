"""
Widget de chat pour l'interface utilisateur
"""
import streamlit as st
import time
from typing import List, Dict, Any, Optional
from ..utils.session_manager import session_manager
from ..utils.api_client import send_message_sync
from ..config.settings import settings


def render_chat_widget():
    """Affiche le widget de chat principal"""
    
    # En-tête du chat
    st.markdown("### 💬 Chat Support Free Mobile")
    
    # Affichage des informations utilisateur
    show_user_info()
    
    # Zone de messages
    render_messages_area()
    
    # Zone de saisie
    render_input_area()
    
    # Liens suggérés
    render_suggested_links()
    
    # Avertissement d'escalade
    render_escalation_warning()


def show_user_info():
    """Affiche les informations utilisateur"""
    user_info = session_manager.get_user_info()
    
    if user_info:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"👤 **{user_info.get('name', 'Utilisateur')}**")
        
        with col2:
            if user_info.get('phone'):
                st.write(f"📱 {user_info.get('phone')}")
        
        with col3:
            if user_info.get('issue_type'):
                st.write(f"📋 {user_info.get('issue_type')}")


def render_messages_area():
    """Affiche la zone des messages"""
    messages = session_manager.get_messages()
    
    # Container pour les messages
    chat_container = st.container()
    
    with chat_container:
        if not messages:
            # Message de bienvenue
            render_welcome_message()
        else:
            # Affichage des messages
            for message in messages:
                render_message(message)
        
        # Indicateur de frappe
        if session_manager.get_typing():
            render_typing_indicator()


def render_welcome_message():
    """Affiche le message de bienvenue"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FF6600, #FF8533);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    ">
        <h4>🆓 Bienvenue sur le Support Free Mobile !</h4>
        <p>Je suis votre assistant virtuel. Comment puis-je vous aider aujourd'hui ?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestions de questions
    st.markdown("#### 💡 Questions fréquentes :")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Comment consulter ma facture ?", key="faq_facture"):
            send_quick_message("Comment consulter ma facture ?")
        
        if st.button("🔧 Problème de connexion", key="faq_connexion"):
            send_quick_message("J'ai un problème de connexion internet")
    
    with col2:
        if st.button("📱 Changer de forfait", key="faq_forfait"):
            send_quick_message("Je veux changer de forfait")
        
        if st.button("❌ Résilier mon contrat", key="faq_resiliation"):
            send_quick_message("Je veux résilier mon contrat")


def render_message(message: Dict[str, Any]):
    """Affiche un message individuel"""
    role = message.get("role", "user")
    content = message.get("content", "")
    timestamp = message.get("timestamp", "")
    metadata = message.get("metadata", {})
    
    if role == "user":
        render_user_message(content, timestamp)
    elif role == "assistant":
        render_assistant_message(content, timestamp, metadata)
    elif role == "system":
        render_system_message(content, timestamp)


def render_user_message(content: str, timestamp: str):
    """Affiche un message utilisateur"""
    st.markdown(f"""
    <div style="
        background: #E3F2FD;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        margin-left: 20%;
        border-left: 4px solid #2196F3;
    ">
        <div style="font-weight: bold; color: #1976D2; margin-bottom: 5px;">
            👤 Vous
        </div>
        <div>{content}</div>
        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
            {format_timestamp(timestamp)}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_assistant_message(content: str, timestamp: str, metadata: Dict[str, Any]):
    """Affiche un message assistant"""
    # Indicateur de confiance
    confidence = metadata.get("confidence", 0.8)
    confidence_color = get_confidence_color(confidence)
    
    st.markdown(f"""
    <div style="
        background: #F5F5F5;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        margin-right: 20%;
        border-left: 4px solid {confidence_color};
    ">
        <div style="font-weight: bold; color: #FF6600; margin-bottom: 5px;">
            🤖 Assistant Free Mobile
        </div>
        <div>{content}</div>
        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
            {format_timestamp(timestamp)}
            <span style="color: {confidence_color}; margin-left: 10px;">
                Confiance: {confidence:.0%}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_system_message(content: str, timestamp: str):
    """Affiche un message système"""
    st.markdown(f"""
    <div style="
        background: #FFF3E0;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #FF9800;
        font-style: italic;
    ">
        <div style="color: #F57C00; font-weight: bold;">
            ℹ️ Système
        </div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_typing_indicator():
    """Affiche l'indicateur de frappe"""
    st.markdown("""
    <div style="
        background: #F5F5F5;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        margin-right: 20%;
        border-left: 4px solid #FF6600;
    ">
        <div style="font-weight: bold; color: #FF6600;">
            🤖 Assistant Free Mobile
        </div>
        <div style="color: #666;">
            <span class="typing-dots">En train d'écrire</span>
            <span class="typing-dots">...</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_input_area():
    """Affiche la zone de saisie"""
    st.markdown("---")
    
    # Zone de saisie
    user_input = st.text_area(
        "Votre message",
        placeholder="Tapez votre message ici...",
        height=100,
        key="user_input"
    )
    
    # Boutons d'action
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📤 Envoyer", type="primary", use_container_width=True):
            if user_input.strip():
                send_message(user_input.strip())
                st.rerun()
            else:
                st.warning("Veuillez saisir un message.")
    
    with col2:
        if st.button("🗑️ Effacer", use_container_width=True):
            session_manager.clear_messages()
            st.rerun()
    
    with col3:
        if st.button("🔄 Nouvelle conversation", use_container_width=True):
            start_new_conversation()
            st.rerun()


def render_suggested_links():
    """Affiche les liens suggérés"""
    suggested_links = session_manager.get_suggested_links()
    
    if suggested_links:
        st.markdown("#### 🔗 Liens utiles :")
        
        for i, link in enumerate(suggested_links):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{link.get('title', 'Lien')}**")
                st.write(link.get('description', ''))
            
            with col2:
                st.link_button(
                    "Ouvrir",
                    link.get('url', '#'),
                    key=f"link_{i}"
                )


def render_escalation_warning():
    """Affiche l'avertissement d'escalade"""
    if session_manager.get_escalation_warning():
        st.warning("""
        ⚠️ **Votre demande nécessite l'intervention d'un agent humain.**
        
        Un agent de notre équipe va prendre en charge votre demande dans les plus brefs délais.
        Vous recevrez une notification dès qu'un agent sera disponible.
        """)


def send_message(message: str):
    """Envoie un message au chatbot"""
    try:
        # Ajout du message utilisateur
        session_manager.add_message("user", message)
        
        # Indicateur de frappe
        session_manager.set_typing(True)
        st.rerun()
        
        # Récupération des informations de session
        user_info = session_manager.get_user_info()
        conversation_id = session_manager.get_conversation_id()
        context_token = session_manager.get_context_token()
        
        # Envoi au backend
        response = send_message_sync(
            message=message,
            conversation_id=conversation_id,
            context_token=context_token,
            user_info=user_info
        )
        
        # Mise à jour de la session
        if response.get("conversation_id"):
            session_manager.set_conversation_id(response["conversation_id"])
        
        if response.get("response"):
            session_manager.add_message(
                "assistant", 
                response["response"]["content"],
                metadata={
                    "confidence": response.get("confidence", 0.8),
                    "needs_escalation": response.get("needs_escalation", False)
                }
            )
        
        # Gestion de l'escalade
        if response.get("needs_escalation"):
            session_manager.set_escalation_warning(True)
            session_manager.add_message(
                "system",
                "Votre demande a été transférée à un agent humain. Vous serez contacté prochainement."
            )
        
        # Liens suggérés
        if response.get("suggested_links"):
            session_manager.set_suggested_links(response["suggested_links"])
        
        # Arrêt de l'indicateur de frappe
        session_manager.set_typing(False)
        
    except Exception as e:
        # Arrêt de l'indicateur de frappe
        session_manager.set_typing(False)
        
        # Message d'erreur
        session_manager.add_message(
            "system",
            f"Désolé, une erreur s'est produite : {str(e)}"
        )


def send_quick_message(message: str):
    """Envoie un message rapide (boutons FAQ)"""
    st.session_state.user_input = message
    send_message(message)


def start_new_conversation():
    """Démarre une nouvelle conversation"""
    session_manager.reset_session()
    session_manager.generate_context_token()


def format_timestamp(timestamp: str) -> str:
    """Formate un timestamp pour l'affichage"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%H:%M")
    except:
        return ""


def get_confidence_color(confidence: float) -> str:
    """Retourne une couleur basée sur le niveau de confiance"""
    if confidence >= 0.8:
        return "#4CAF50"  # Vert
    elif confidence >= 0.6:
        return "#FF9800"  # Orange
    else:
        return "#F44336"  # Rouge


