"""
Page d'analytics et monitoring
"""
import streamlit as st
from datetime import datetime, timedelta
from ..components.analytics_charts import AnalyticsCharts
from ..utils.api_client import get_analytics_sync, get_ai_stats_sync, health_check_sync
from ..config.settings import settings


def render():
    """Rend la page d'analytics"""
    
    # Configuration de la page
    st.set_page_config(
        page_title="Analytics - Free Mobile",
        page_icon="📊",
        layout="wide"
    )
    
    # En-tête
    st.title("📊 Analytics & Monitoring")
    st.markdown("Tableau de bord en temps réel du système de support")
    
    # Sélecteur de période
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        start_date = st.date_input(
            "Date de début",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "Date de fin",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    with col3:
        if st.button("🔄 Actualiser", use_container_width=True):
            st.rerun()
    
    # Vérification de la période
    if start_date > end_date:
        st.error("La date de début doit être antérieure à la date de fin.")
        return
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        try:
            # Analytics principales
            analytics_data = get_analytics_sync(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            # Statistiques IA
            ai_stats = get_ai_stats_sync()
            
            # Statut de santé
            health_status = health_check_sync()
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {str(e)}")
            return
    
    # Affichage des données
    if analytics_data:
        # Cartes KPI
        st.markdown("### 📈 Indicateurs Clés de Performance")
        AnalyticsCharts.render_kpi_cards(analytics_data.get("kpis", {}))
        
        # Graphiques principaux
        col1, col2 = st.columns(2)
        
        with col1:
            # Timeline des conversations
            AnalyticsCharts.render_conversations_timeline(
                analytics_data.get("conversations_timeline", [])
            )
        
        with col2:
            # Distribution des intentions
            AnalyticsCharts.render_intent_distribution(
                analytics_data.get("intent_distribution", [])
            )
        
        # Graphiques secondaires
        col1, col2 = st.columns(2)
        
        with col1:
            # Statuts des tickets
            AnalyticsCharts.render_ticket_status(
                analytics_data.get("ticket_status", [])
            )
        
        with col2:
            # Activité par heure
            AnalyticsCharts.render_hourly_activity(
                analytics_data.get("hourly_activity", [])
            )
        
        # Métriques de performance
        st.markdown("### ⚡ Métriques de Performance")
        AnalyticsCharts.render_performance_metrics(
            analytics_data.get("performance", {})
        )
        
        # Gauge de satisfaction
        col1, col2 = st.columns([1, 1])
        
        with col1:
            AnalyticsCharts.render_satisfaction_gauge(
                analytics_data.get("satisfaction_gauge", {})
            )
        
        with col2:
            # Statut de santé des services
            AnalyticsCharts.render_health_status(health_status)
    
    # Statistiques IA
    if ai_stats:
        st.markdown("### 🤖 Intelligence Artificielle")
        AnalyticsCharts.render_ai_stats(ai_stats)
    
    # Boutons d'export
    st.markdown("### 📊 Export des Données")
    AnalyticsCharts.render_export_buttons()
    
    # Informations de session
    with st.expander("ℹ️ Informations de Session", expanded=False):
        st.json({
            "Période analysée": f"{start_date} - {end_date}",
            "Dernière actualisation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Statut des services": health_status.get("overall", "unknown")
        })
    
    # Pied de page
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>📊 Free Mobile Analytics - Données mises à jour en temps réel</p>
    </div>
    """, unsafe_allow_html=True)


