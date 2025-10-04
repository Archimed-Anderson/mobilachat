"""
Formulaire de contact pour collecter les informations utilisateur
"""
import streamlit as st
import re
from typing import Dict, Any, Optional
from ..utils.session_manager import session_manager


def render_contact_form() -> Optional[Dict[str, Any]]:
    """Affiche le formulaire de contact et retourne les informations saisies"""
    
    st.markdown("### 📝 Informations de Contact")
    st.markdown("Veuillez remplir ces informations pour personnaliser votre expérience.")
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nom complet *",
                placeholder="Votre nom et prénom",
                help="Votre nom complet pour personnaliser les réponses"
            )
            
            phone = st.text_input(
                "Numéro de téléphone *",
                placeholder="06 12 34 56 78",
                help="Votre numéro de téléphone Free Mobile"
            )
        
        with col2:
            email = st.text_input(
                "Email (optionnel)",
                placeholder="votre@email.com",
                help="Votre adresse email pour les notifications"
            )
            
            company = st.text_input(
                "Entreprise (optionnel)",
                placeholder="Nom de votre entreprise",
                help="Si vous appelez pour votre entreprise"
            )
        
        # Informations supplémentaires
        st.markdown("#### Informations Supplémentaires")
        
        col3, col4 = st.columns(2)
        
        with col3:
            issue_type = st.selectbox(
                "Type de demande",
                ["Général", "Facturation", "Technique", "Forfait", "Résiliation", "Autre"],
                help="Sélectionnez le type de votre demande"
            )
        
        with col4:
            urgency = st.selectbox(
                "Urgence",
                ["Faible", "Normale", "Élevée", "Critique"],
                help="Niveau d'urgence de votre demande"
            )
        
        # Message optionnel
        message = st.text_area(
            "Message (optionnel)",
            placeholder="Décrivez brièvement votre demande...",
            help="Vous pouvez donner plus de détails sur votre demande"
        )
        
        # Boutons
        col5, col6, col7 = st.columns([1, 1, 2])
        
        with col5:
            submit_button = st.form_submit_button(
                "Continuer",
                type="primary",
                use_container_width=True
            )
        
        with col6:
            skip_button = st.form_submit_button(
                "Passer",
                use_container_width=True
            )
    
    # Validation et traitement
    if submit_button:
        if validate_form(name, phone, email):
            user_info = {
                "name": name.strip(),
                "phone": clean_phone_number(phone),
                "email": email.strip() if email else None,
                "company": company.strip() if company else None,
                "issue_type": issue_type,
                "urgency": urgency,
                "message": message.strip() if message else None,
                "timestamp": st.session_state.get("current_time", "unknown")
            }
            
            # Sauvegarde dans la session
            session_manager.set_user_info(user_info)
            
            st.success("✅ Informations enregistrées avec succès !")
            st.rerun()
            
            return user_info
        else:
            st.error("❌ Veuillez corriger les erreurs dans le formulaire.")
            return None
    
    elif skip_button:
        # Utilisateur anonyme
        user_info = {
            "name": "Utilisateur anonyme",
            "phone": None,
            "email": None,
            "company": None,
            "issue_type": "Général",
            "urgency": "Normale",
            "message": None,
            "timestamp": st.session_state.get("current_time", "unknown")
        }
        
        session_manager.set_user_info(user_info)
        st.info("ℹ️ Vous continuez en mode anonyme.")
        st.rerun()
        
        return user_info
    
    return None


def validate_form(name: str, phone: str, email: str) -> bool:
    """Valide le formulaire de contact"""
    errors = []
    
    # Validation du nom
    if not name or len(name.strip()) < 2:
        errors.append("Le nom doit contenir au moins 2 caractères.")
    
    # Validation du téléphone
    if not phone or not is_valid_phone(phone):
        errors.append("Veuillez saisir un numéro de téléphone valide (format français).")
    
    # Validation de l'email (si fourni)
    if email and not is_valid_email(email):
        errors.append("Veuillez saisir une adresse email valide.")
    
    # Affichage des erreurs
    if errors:
        for error in errors:
            st.error(error)
        return False
    
    return True


def is_valid_phone(phone: str) -> bool:
    """Valide un numéro de téléphone français"""
    # Nettoyage du numéro
    clean_phone = re.sub(r'[^\d]', '', phone)
    
    # Vérification des formats français
    patterns = [
        r'^0[1-9]\d{8}$',  # 06 12 34 56 78
        r'^\+33[1-9]\d{8}$',  # +33 6 12 34 56 78
        r'^33[1-9]\d{8}$'  # 33 6 12 34 56 78
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)


def is_valid_email(email: str) -> bool:
    """Valide une adresse email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def clean_phone_number(phone: str) -> str:
    """Nettoie et formate un numéro de téléphone"""
    # Suppression de tous les caractères non numériques
    clean_phone = re.sub(r'[^\d]', '', phone)
    
    # Formatage selon le type
    if clean_phone.startswith('33'):
        # Format international sans +
        return f"+{clean_phone}"
    elif clean_phone.startswith('0'):
        # Format national
        return clean_phone
    elif len(clean_phone) == 9:
        # Format sans indicatif
        return f"0{clean_phone}"
    else:
        # Format par défaut
        return clean_phone


def show_user_info():
    """Affiche les informations utilisateur actuelles"""
    user_info = session_manager.get_user_info()
    
    if user_info and user_info.get("name") != "Utilisateur anonyme":
        with st.expander("👤 Informations de contact", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Nom :** {user_info.get('name', 'N/A')}")
                st.write(f"**Téléphone :** {user_info.get('phone', 'N/A')}")
            
            with col2:
                st.write(f"**Email :** {user_info.get('email', 'N/A')}")
                st.write(f"**Type de demande :** {user_info.get('issue_type', 'N/A')}")
            
            if st.button("Modifier les informations", key="edit_user_info"):
                session_manager.reset_session()
                st.rerun()


