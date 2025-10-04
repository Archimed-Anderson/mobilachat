"""
Détecteur de réclamations pour les posts Mastodon
"""
import re
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ComplaintDetector:
    def __init__(self):
        # Mots-clés de réclamation
        self.complaint_keywords = [
            "nul", "nulle", "horrible", "terrible", "catastrophe", "désastre",
            "mauvais", "mal", "malheureux", "déçu", "décevant", "frustrant",
            "énervant", "agacé", "fâché", "en colère", "furieux", "exaspéré",
            "dégoûté", "révolté", "scandalisé", "indigné", "outré",
            "problème", "bug", "erreur", "dysfonctionnement", "panne",
            "plainte", "réclamation", "rémunération", "dédommagement"
        ]
        
        # Emojis négatifs
        self.negative_emojis = [
            "😠", "😡", "🤬", "😤", "😞", "😢", "😭", "👎", "❌", "💔", "😒",
            "🤮", "🤢", "😤", "😠", "😡", "🤬", "😤", "😞", "😢", "😭"
        ]
        
        # Patterns de réclamation
        self.complaint_patterns = [
            r"je.*suis.*déçu",
            r"c'est.*nul",
            r"ça.*marche.*pas",
            r"service.*client.*nul",
            r"free.*mobile.*nul",
            r"jamais.*plus.*free",
            r"je.*vais.*changer",
            r"résilier.*contrat",
            r"plainte.*contre",
            r"réclamation.*free"
        ]
        
        # Mots d'intensification
        self.intensifiers = [
            "très", "vraiment", "extrêmement", "totalement", "complètement",
            "absolument", "carrément", "franchement", "sérieusement"
        ]
        
        # Mots de négation
        self.negations = [
            "pas", "ne", "n'", "jamais", "rien", "aucun", "nul", "nulle"
        ]
    
    def detect_complaint(self, content: str) -> Dict[str, Any]:
        """Détecte si un post est une réclamation"""
        try:
            content_lower = content.lower()
            
            # Calcul du score de réclamation
            complaint_score = self._calculate_complaint_score(content_lower)
            
            # Détection des mots-clés
            found_keywords = self._find_complaint_keywords(content_lower)
            
            # Détection des patterns
            found_patterns = self._find_complaint_patterns(content_lower)
            
            # Détection des emojis négatifs
            negative_emoji_count = self._count_negative_emojis(content)
            
            # Détection de la négation
            has_negation = self._has_negation(content_lower)
            
            # Calcul de l'urgence
            urgency = self._calculate_urgency(
                complaint_score, 
                negative_emoji_count, 
                len(found_keywords),
                len(found_patterns)
            )
            
            # Détermination du type de réclamation
            complaint_type = self._classify_complaint_type(content_lower, found_keywords)
            
            # Calcul de la confiance
            confidence = min(complaint_score / 10.0, 1.0)
            
            return {
                "is_complaint": complaint_score >= 3.0,
                "complaint_score": complaint_score,
                "confidence": confidence,
                "urgency": urgency,
                "type": complaint_type,
                "keywords_found": found_keywords,
                "patterns_found": found_patterns,
                "negative_emoji_count": negative_emoji_count,
                "has_negation": has_negation,
                "sentiment": self._analyze_sentiment(content_lower, complaint_score)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de réclamation: {e}")
            return {
                "is_complaint": False,
                "complaint_score": 0.0,
                "confidence": 0.0,
                "urgency": "low",
                "type": "unknown",
                "keywords_found": [],
                "patterns_found": [],
                "negative_emoji_count": 0,
                "has_negation": False,
                "sentiment": "neutral"
            }
    
    def _calculate_complaint_score(self, content: str) -> float:
        """Calcule le score de réclamation"""
        score = 0.0
        
        # Score des mots-clés
        for keyword in self.complaint_keywords:
            if keyword in content:
                score += 1.0
                # Bonus pour les mots-clés forts
                if keyword in ["nul", "horrible", "terrible", "catastrophe"]:
                    score += 0.5
        
        # Score des patterns
        for pattern in self.complaint_patterns:
            if re.search(pattern, content):
                score += 2.0
        
        # Score des emojis négatifs
        emoji_count = self._count_negative_emojis(content)
        score += emoji_count * 0.5
        
        # Bonus pour la répétition
        for keyword in self.complaint_keywords:
            count = content.count(keyword)
            if count > 1:
                score += (count - 1) * 0.3
        
        # Bonus pour les majuscules (cri)
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if caps_ratio > 0.3:
            score += 1.0
        
        # Bonus pour les points d'exclamation
        exclamation_count = content.count('!')
        score += exclamation_count * 0.2
        
        return score
    
    def _find_complaint_keywords(self, content: str) -> List[str]:
        """Trouve les mots-clés de réclamation dans le contenu"""
        found_keywords = []
        for keyword in self.complaint_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        return found_keywords
    
    def _find_complaint_patterns(self, content: str) -> List[str]:
        """Trouve les patterns de réclamation dans le contenu"""
        found_patterns = []
        for pattern in self.complaint_patterns:
            if re.search(pattern, content):
                found_patterns.append(pattern)
        return found_patterns
    
    def _count_negative_emojis(self, content: str) -> int:
        """Compte les emojis négatifs dans le contenu"""
        count = 0
        for emoji in self.negative_emojis:
            count += content.count(emoji)
        return count
    
    def _has_negation(self, content: str) -> bool:
        """Détecte la présence de négations"""
        for negation in self.negations:
            if negation in content:
                return True
        return False
    
    def _calculate_urgency(
        self, 
        complaint_score: float, 
        emoji_count: int, 
        keyword_count: int, 
        pattern_count: int
    ) -> str:
        """Calcule le niveau d'urgence"""
        urgency_score = complaint_score + (emoji_count * 0.5) + (keyword_count * 0.3) + (pattern_count * 0.5)
        
        if urgency_score >= 8:
            return "urgent"
        elif urgency_score >= 5:
            return "high"
        elif urgency_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _classify_complaint_type(self, content: str, keywords: List[str]) -> str:
        """Classifie le type de réclamation"""
        # Facturation
        billing_keywords = ["facture", "facturation", "paiement", "prélèvement", "coût", "prix"]
        if any(keyword in content for keyword in billing_keywords):
            return "billing"
        
        # Technique
        tech_keywords = ["problème", "bug", "erreur", "connexion", "réseau", "signal", "wifi"]
        if any(keyword in content for keyword in tech_keywords):
            return "technical"
        
        # Service client
        service_keywords = ["service", "client", "support", "aide", "réponse", "attente"]
        if any(keyword in content for keyword in service_keywords):
            return "customer_service"
        
        # Résiliation
        cancellation_keywords = ["résilier", "annuler", "arrêter", "changer", "opérateur"]
        if any(keyword in content for keyword in cancellation_keywords):
            return "cancellation"
        
        # Général
        return "general"
    
    def _analyze_sentiment(self, content: str, complaint_score: float) -> str:
        """Analyse le sentiment du contenu"""
        if complaint_score >= 5:
            return "very_negative"
        elif complaint_score >= 3:
            return "negative"
        elif complaint_score >= 1:
            return "slightly_negative"
        else:
            return "neutral"
    
    def get_complaint_examples(self) -> List[Dict[str, str]]:
        """Retourne des exemples de réclamations"""
        return [
            {
                "content": "Free Mobile c'est nul, ça marche jamais !",
                "type": "technical",
                "urgency": "high"
            },
            {
                "content": "Je suis déçu de Free Mobile, service client inexistant",
                "type": "customer_service",
                "urgency": "medium"
            },
            {
                "content": "Ma facture Free Mobile est trop chère, je vais résilier",
                "type": "billing",
                "urgency": "high"
            },
            {
                "content": "Problème de connexion Free Mobile depuis 3 jours",
                "type": "technical",
                "urgency": "medium"
            }
        ]
    
    def get_detection_stats(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les statistiques de détection sur une liste de posts"""
        if not posts:
            return {"total": 0, "complaints": 0, "complaint_rate": 0.0}
        
        total_posts = len(posts)
        complaint_count = 0
        urgency_counts = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
        type_counts = {}
        
        for post in posts:
            result = self.detect_complaint(post.get("content", ""))
            if result["is_complaint"]:
                complaint_count += 1
                urgency_counts[result["urgency"]] += 1
                complaint_type = result["type"]
                type_counts[complaint_type] = type_counts.get(complaint_type, 0) + 1
        
        return {
            "total": total_posts,
            "complaints": complaint_count,
            "complaint_rate": (complaint_count / total_posts) * 100 if total_posts > 0 else 0,
            "urgency_distribution": urgency_counts,
            "type_distribution": type_counts
        }


