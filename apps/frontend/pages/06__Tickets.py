"""
Page de gestion des tickets
"""
import streamlit as st
from ..utils.api_client import get_tickets_sync
from ..config.settings import settings


def render():
    """Rend la page de gestion des tickets"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Tickets - Free Mobile",
        page_icon="🎫",
        layout="wide"
    )
    
    # En-tête
    st.title("🎫 Gestion des Tickets")
    st.markdown("Suivez et gérez les tickets de support")
    
    # Filtres
    st.markdown("### 🔍 Filtres")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Statut",
            ["Tous", "OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
            index=0
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Priorité",
            ["Tous", "LOW", "MEDIUM", "HIGH", "URGENT"],
            index=0
        )
    
    with col3:
        page_size = st.selectbox(
            "Taille de page",
            [10, 20, 50, 100],
            index=1
        )
    
    with col4:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    
    # Chargement des tickets
    with st.spinner("Chargement des tickets..."):
        try:
            tickets_data = get_tickets_sync(
                status=status_filter if status_filter != "Tous" else None,
                priority=priority_filter if priority_filter != "Tous" else None,
                page=1,
                size=page_size
            )
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des tickets : {str(e)}")
            return
    
    # Affichage des tickets
    if tickets_data and tickets_data.get("tickets"):
        tickets = tickets_data["tickets"]
        total = tickets_data.get("total", 0)
        
        st.markdown(f"### 📋 Tickets ({total} total)")
        
        # Statistiques rapides
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            open_count = sum(1 for t in tickets if t.get("status") == "OPEN")
            st.metric("Ouverts", open_count)
        
        with col2:
            in_progress_count = sum(1 for t in tickets if t.get("status") == "IN_PROGRESS")
            st.metric("En cours", in_progress_count)
        
        with col3:
            resolved_count = sum(1 for t in tickets if t.get("status") == "RESOLVED")
            st.metric("Résolus", resolved_count)
        
        with col4:
            urgent_count = sum(1 for t in tickets if t.get("priority") == "URGENT")
            st.metric("Urgents", urgent_count)
        
        # Tableau des tickets
        st.markdown("### 📊 Liste des Tickets")
        
        for ticket in tickets:
            render_ticket_card(ticket)
    
    else:
        st.info("Aucun ticket trouvé avec les filtres sélectionnés.")
    
    # Pied de page
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>🎫 Free Mobile - Gestion des Tickets</p>
    </div>
    """, unsafe_allow_html=True)


def render_ticket_card(ticket):
    """Affiche une carte de ticket"""
    
    # Couleurs selon la priorité
    priority_colors = {
        "LOW": "🟢",
        "MEDIUM": "🟡", 
        "HIGH": "🟠",
        "URGENT": "🔴"
    }
    
    # Couleurs selon le statut
    status_colors = {
        "OPEN": "🔴",
        "IN_PROGRESS": "🟡",
        "RESOLVED": "🟢",
        "CLOSED": "⚫"
    }
    
    priority = ticket.get("priority", "MEDIUM")
    status = ticket.get("status", "OPEN")
    
    with st.expander(
        f"{priority_colors.get(priority, '⚪')} {status_colors.get(status, '⚪')} "
        f"Ticket #{ticket.get('id', 'N/A')[:8]}... - {priority} - {status}",
        expanded=False
    ):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**ID :** {ticket.get('id', 'N/A')}")
            st.write(f"**Priorité :** {priority}")
            st.write(f"**Statut :** {status}")
            st.write(f"**Catégorie :** {ticket.get('category', 'N/A')}")
        
        with col2:
            st.write(f"**Conversation :** {ticket.get('conversation_id', 'N/A')[:8]}...")
            st.write(f"**Assigné à :** {ticket.get('assigned_to', 'Non assigné')}")
            st.write(f"**Créé le :** {format_date(ticket.get('created_at', ''))}")
            st.write(f"**Modifié le :** {format_date(ticket.get('updated_at', ''))}")
        
        # Notes de résolution
        if ticket.get('resolution_notes'):
            st.markdown("**Notes de résolution :**")
            st.write(ticket.get('resolution_notes'))
        
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"👁️ Voir", key=f"view_{ticket.get('id')}"):
                st.info("Fonctionnalité de visualisation en cours de développement")
        
        with col2:
            if st.button(f"✏️ Modifier", key=f"edit_{ticket.get('id')}"):
                st.info("Fonctionnalité de modification en cours de développement")
        
        with col3:
            if st.button(f"💬 Conversation", key=f"conv_{ticket.get('id')}"):
                st.info("Fonctionnalité de conversation en cours de développement")


def format_date(date_str):
    """Formate une date pour l'affichage"""
    if not date_str:
        return "N/A"
    
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return date_str


