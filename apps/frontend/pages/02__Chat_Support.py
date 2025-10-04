"""
Page de chat support
"""
import streamlit as st
from ..components.chat_widget import render_chat_widget
from ..components.contact_form import render_contact_form, show_user_info
from ..utils.session_manager import session_manager
from ..config.settings import settings


def render():
    """Rend la page de chat support"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Chat Support - Free Mobile",
        page_icon="💬",
        layout="wide"
    )
    
    # En-tête
    st.title("💬 Chat Support Free Mobile")
    st.markdown("Posez vos questions à notre assistant virtuel intelligent")
    
    # Vérification de la session
    if not session_manager.is_session_valid():
        st.warning("⚠️ Votre session a expiré. Veuillez actualiser la page.")
        return
    
    # Vérification des informations utilisateur
    user_info = session_manager.get_user_info()
    
    if not user_info or user_info.get("name") == "Utilisateur anonyme":
        # Affichage du formulaire de contact
        st.markdown("---")
        user_info = render_contact_form()
        
        if not user_info:
            st.stop()
    else:
        # Affichage des informations utilisateur
        show_user_info()
    
    # Widget de chat
    st.markdown("---")
    render_chat_widget()
    
    # Pied de page
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>🆓 Free Mobile - Support Client Intelligent</p>
        <p>Assistance 24h/24, 7j/7</p>
    </div>
    """, unsafe_allow_html=True)


