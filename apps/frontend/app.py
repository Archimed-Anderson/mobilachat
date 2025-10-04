"""
Application Streamlit principale
"""
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
from datetime import datetime
import sys
from pathlib import Path

# Ajout du chemin du projet
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from .config.settings import settings
from .utils.session_manager import session_manager
from .pages import chat_support, analytics, tickets


def main():
    """Fonction principale de l'application"""
    
    # Configuration de la page
    st.set_page_config(
        page_title=settings.PAGE_TITLE,
        page_icon=settings.PAGE_ICON,
        layout=settings.LAYOUT,
        initial_sidebar_state=settings.SIDEBAR_STATE
    )
    
    # CSS personnalisé
    load_custom_css()
    
    # Initialisation de la session
    session_manager._initialize_session()
    
    # En-tête principal
    render_header()
    
    # Menu de navigation
    selected_page = render_navigation()
    
    # Contenu principal
    render_main_content(selected_page)
    
    # Pied de page
    render_footer()


def load_custom_css():
    """Charge le CSS personnalisé"""
    st.markdown("""
    <style>
    /* Couleurs Free Mobile */
    :root {
        --primary-color: #FF6600;
        --secondary-color: #F0F0F0;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --info-color: #2196F3;
    }
    
    /* En-tête principal */
    .main-header {
        background: linear-gradient(135deg, #FF6600, #FF8533);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
    }
    
    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.2em;
        opacity: 0.9;
    }
    
    /* Cartes */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
    }
    
    /* Boutons */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #E55A00;
        color: white;
    }
    
    /* Messages de chat */
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .chat-message.user {
        background: #E3F2FD;
        margin-left: 20%;
        border-left: 4px solid #2196F3;
    }
    
    .chat-message.assistant {
        background: #F5F5F5;
        margin-right: 20%;
        border-left: 4px solid var(--primary-color);
    }
    
    /* Indicateur de frappe */
    .typing-dots::after {
        content: '';
        animation: typing 1.5s infinite;
    }
    
    @keyframes typing {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Métriques */
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    
    .metric-item {
        text-align: center;
        padding: 15px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Alertes */
    .alert {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    
    /* Pied de page */
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9em;
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Affiche l'en-tête principal"""
    st.markdown(f"""
    <div class="main-header">
        <h1>{settings.PAGE_ICON} {settings.PAGE_TITLE}</h1>
        <p>Support Client Intelligent avec IA</p>
    </div>
    """, unsafe_allow_html=True)


def render_navigation():
    """Affiche le menu de navigation"""
    
    # Menu principal
    selected_page = option_menu(
        menu_title=None,
        options=["💬 Chat", "📊 Analytics", "🎫 Tickets", "⚙️ Configuration"],
        icons=["chat-dots", "graph-up", "ticket", "gear"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#FF6600", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {"background-color": "#FF6600"},
        }
    )
    
    return selected_page


def render_main_content(selected_page):
    """Affiche le contenu principal selon la page sélectionnée"""
    
    if selected_page == "💬 Chat":
        chat_support.render()
    
    elif selected_page == "📊 Analytics":
        analytics.render()
    
    elif selected_page == "🎫 Tickets":
        tickets.render()
    
    elif selected_page == "⚙️ Configuration":
        render_configuration_page()


def render_configuration_page():
    """Affiche la page de configuration"""
    
    st.title("⚙️ Configuration")
    
    # Informations de session
    with st.expander("📋 Informations de Session", expanded=True):
        session_data = session_manager.get_session_data()
        st.json(session_data)
    
    # Configuration de l'application
    with st.expander("🔧 Configuration de l'Application", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Version :** {settings.VERSION}")
            st.write(f"**Mode Debug :** {settings.DEBUG}")
            st.write(f"**Timeout Session :** {settings.SESSION_TIMEOUT}s")
        
        with col2:
            st.write(f"**Backend URL :** {settings.BACKEND_API_URL}")
            st.write(f"**AI Engine URL :** {settings.AI_ENGINE_URL}")
            st.write(f"**Refresh Interval :** {settings.REFRESH_INTERVAL}s")
    
    # Actions de session
    with st.expander("🔄 Actions de Session", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Actualiser", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ Effacer Session", use_container_width=True):
                session_manager.reset_session()
                st.success("Session effacée !")
                st.rerun()
        
        with col3:
            if st.button("📊 Statistiques", use_container_width=True):
                st.info("Fonctionnalité de statistiques en cours de développement")
    
    # Informations système
    with st.expander("ℹ️ Informations Système", expanded=False):
        st.write(f"**Timestamp :** {datetime.now().isoformat()}")
        st.write(f"**User Agent :** {st.get_option('browser.gatherUsageStats')}")
        st.write(f"**Streamlit Version :** {st.__version__}")


def render_footer():
    """Affiche le pied de page"""
    st.markdown("""
    <div class="footer">
        <p>🆓 Free Mobile - Support Client Intelligent</p>
        <p>Version {version} | © 2024 Free Mobile</p>
    </div>
    """.format(version=settings.VERSION), unsafe_allow_html=True)


if __name__ == "__main__":
    main()


