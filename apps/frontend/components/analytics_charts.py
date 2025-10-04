"""
Composants de graphiques pour les analytics
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta


class AnalyticsCharts:
    """Classe pour générer les graphiques d'analytics"""
    
    @staticmethod
    def render_kpi_cards(kpis: Dict[str, Any]):
        """Affiche les cartes KPI"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💬 Conversations",
                value=kpis.get("total_conversations", 0),
                delta=kpis.get("conversations_change", 0)
            )
        
        with col2:
            st.metric(
                label="🎫 Tickets Ouverts",
                value=kpis.get("open_tickets", 0),
                delta=kpis.get("tickets_change", 0)
            )
        
        with col3:
            st.metric(
                label="✅ Taux de Résolution",
                value=f"{kpis.get('resolution_rate', 0):.1f}%",
                delta=f"{kpis.get('resolution_change', 0):.1f}%"
            )
        
        with col4:
            st.metric(
                label="⏱️ Temps de Réponse",
                value=f"{kpis.get('avg_response_time', 0):.1f} min",
                delta=f"{kpis.get('response_time_change', 0):.1f} min"
            )
    
    @staticmethod
    def render_conversations_timeline(timeline_data: List[Dict[str, Any]]):
        """Affiche le graphique de timeline des conversations"""
        if not timeline_data:
            st.info("Aucune donnée de timeline disponible")
            return
        
        df = pd.DataFrame(timeline_data)
        df['date'] = pd.to_datetime(df['date'])
        
        fig = px.line(
            df, 
            x='date', 
            y='conversations',
            title="📈 Évolution des Conversations",
            labels={'conversations': 'Nombre de conversations', 'date': 'Date'}
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Conversations",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_intent_distribution(intent_data: List[Dict[str, Any]]):
        """Affiche la distribution des intentions"""
        if not intent_data:
            st.info("Aucune donnée d'intention disponible")
            return
        
        df = pd.DataFrame(intent_data)
        
        fig = px.pie(
            df,
            values='count',
            names='intent',
            title="🎯 Distribution des Intentions",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_ticket_status(ticket_data: List[Dict[str, Any]]):
        """Affiche la répartition des statuts de tickets"""
        if not ticket_data:
            st.info("Aucune donnée de tickets disponible")
            return
        
        df = pd.DataFrame(ticket_data)
        
        # Mapping des couleurs pour les statuts
        status_colors = {
            'OPEN': '#FF9800',
            'IN_PROGRESS': '#2196F3',
            'RESOLVED': '#4CAF50',
            'CLOSED': '#9E9E9E'
        }
        
        fig = px.bar(
            df,
            x='status',
            y='count',
            title="🎫 Statuts des Tickets",
            color='status',
            color_discrete_map=status_colors
        )
        
        fig.update_layout(
            xaxis_title="Statut",
            yaxis_title="Nombre de tickets",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_hourly_activity(hourly_data: List[Dict[str, Any]]):
        """Affiche l'activité par heure"""
        if not hourly_data:
            st.info("Aucune donnée d'activité horaire disponible")
            return
        
        df = pd.DataFrame(hourly_data)
        
        fig = px.bar(
            df,
            x='hour',
            y='messages',
            title="🕐 Activité par Heure",
            color='messages',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Heure",
            yaxis_title="Nombre de messages",
            xaxis=dict(tickmode='linear', tick0=0, dtick=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_satisfaction_gauge(satisfaction_data: Dict[str, Any]):
        """Affiche le gauge de satisfaction"""
        if not satisfaction_data:
            st.info("Aucune donnée de satisfaction disponible")
            return
        
        value = satisfaction_data.get('value', 0)
        max_value = satisfaction_data.get('max', 5)
        label = satisfaction_data.get('label', 'Satisfaction')
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': label},
            delta={'reference': 4.0},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 2], 'color': "lightgray"},
                    {'range': [2, 4], 'color': "yellow"},
                    {'range': [4, max_value], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 4.5
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_performance_metrics(performance_data: Dict[str, Any]):
        """Affiche les métriques de performance"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="📊 Total Messages",
                value=performance_data.get('total_messages', 0)
            )
        
        with col2:
            st.metric(
                label="⏱️ Temps de Résolution Moyen",
                value=f"{performance_data.get('avg_resolution_time', 0):.1f} h"
            )
        
        # Graphique de taux d'escalade
        escalation_rate = performance_data.get('escalation_rate', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=escalation_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Taux d'Escalade (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 20], 'color': "green"},
                    {'range': [20, 40], 'color': "yellow"},
                    {'range': [40, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_ai_stats(ai_stats: Dict[str, Any]):
        """Affiche les statistiques du moteur IA"""
        st.markdown("#### 🤖 Statistiques du Moteur IA")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="📚 Documents Indexés",
                value=ai_stats.get('vector_store_stats', {}).get('total_documents', 0)
            )
        
        with col2:
            st.metric(
                label="🎯 Seuil de Similarité",
                value=f"{ai_stats.get('vector_store_stats', {}).get('similarity_threshold', 0):.2f}"
            )
        
        with col3:
            status = ai_stats.get('system_status', 'unknown')
            status_color = "green" if status == "healthy" else "red"
            st.markdown(f"**Statut :** <span style='color: {status_color}'>{status}</span>", unsafe_allow_html=True)
        
        # Informations sur les modèles
        model_info = ai_stats.get('model_info', {})
        
        st.markdown("#### 🔧 Configuration des Modèles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Modèle LLM :** {model_info.get('llm_model', 'N/A')}")
            st.write(f"**Modèle d'Embedding :** {model_info.get('embedding_model', 'N/A')}")
        
        with col2:
            st.write(f"**Device :** {model_info.get('device', 'N/A')}")
            st.write(f"**Température :** {model_info.get('temperature', 'N/A')}")
    
    @staticmethod
    def render_health_status(health_data: Dict[str, Any]):
        """Affiche le statut de santé des services"""
        st.markdown("#### 🏥 Statut des Services")
        
        services = ['backend', 'ai_engine']
        
        for service in services:
            service_data = health_data.get(service, {})
            status = service_data.get('status', 'unknown')
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{service.title()}**")
            
            with col2:
                if status == 'healthy':
                    st.success("✅ En ligne")
                else:
                    st.error("❌ Hors ligne")
            
            with col3:
                if 'version' in service_data:
                    st.write(f"v{service_data['version']}")
    
    @staticmethod
    def render_export_buttons():
        """Affiche les boutons d'export"""
        st.markdown("#### 📊 Export des Données")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export PDF", use_container_width=True):
                st.info("Fonctionnalité d'export PDF en cours de développement")
        
        with col2:
            if st.button("📊 Export Excel", use_container_width=True):
                st.info("Fonctionnalité d'export Excel en cours de développement")
        
        with col3:
            if st.button("📈 Export CSV", use_container_width=True):
                st.info("Fonctionnalité d'export CSV en cours de développement")


