"""
Analyseur de sentiment pour détecter l'état émotionnel des messages
"""
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    def __init__(self):
        # Mots-clés et patterns pour l'analyse de sentiment
        self.positive_patterns = {
            "keywords": [
                "merci", "parfait", "excellent", "super", "génial", "fantastique",
                "bien", "bon", "satisfait", "content", "heureux", "ravi",
                "apprécier", "aimer", "adorer", "recommandé", "conseiller",
                "bravo", "félicitations", "chapeau", "top", "cool", "sympa"
            ],
            "emojis": ["😊", "😄", "😃", "😁", "😍", "🥰", "😘", "👍", "👏", "🎉", "✅"],
            "patterns": [
                r"très.*bien",
                r"parfait.*service",
                r"excellent.*travail",
                r"je.*suis.*satisfait",
                r"merci.*beaucoup"
            ]
        }
        
        self.negative_patterns = {
            "keywords": [
                "nul", "nulle", "horrible", "terrible", "catastrophe", "désastre",
                "mauvais", "mal", "malheureux", "déçu", "décevant", "frustrant",
                "énervant", "agacé", "fâché", "en colère", "furieux", "exaspéré",
                "dégoûté", "révolté", "scandalisé", "indigné", "outré",
                "problème", "bug", "erreur", "dysfonctionnement", "panne"
            ],
            "emojis": ["😠", "😡", "🤬", "😤", "😞", "😢", "😭", "👎", "❌", "💔", "😒"],
            "patterns": [
                r"je.*suis.*déçu",
                r"c'est.*nul",
                r"ça.*marche.*pas",
                r"problème.*grave",
                r"service.*client.*nul"
            ]
        }
        
        self.neutral_patterns = {
            "keywords": [
                "question", "demande", "information", "renseignement",
                "comment", "pourquoi", "quand", "où", "combien",
                "besoin", "vouloir", "souhaiter", "désirer"
            ],
            "patterns": [
                r"j'ai.*une.*question",
                r"je.*voudrais.*savoir",
                r"pouvez.*vous.*m'aider",
                r"j'aimerais.*connaître"
            ]
        }
        
        # Mots d'intensification
        self.intensifiers = {
            "positive": ["très", "vraiment", "extrêmement", "totalement", "complètement"],
            "negative": ["très", "vraiment", "extrêmement", "totalement", "complètement", "absolument"]
        }
        
        # Mots de négation
        self.negations = ["pas", "ne", "n'", "jamais", "rien", "aucun", "nul"]
    
    def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyse le sentiment d'un message"""
        try:
            message_lower = message.lower()
            
            # Calcul des scores pour chaque sentiment
            positive_score = self._calculate_sentiment_score(message_lower, self.positive_patterns)
            negative_score = self._calculate_sentiment_score(message_lower, self.negative_patterns)
            neutral_score = self._calculate_sentiment_score(message_lower, self.neutral_patterns)
            
            # Application des modificateurs
            positive_score = self._apply_modifiers(message_lower, positive_score, "positive")
            negative_score = self._apply_modifiers(message_lower, negative_score, "negative")
            
            # Détection des négations
            if self._has_negation(message_lower):
                # Inversion des scores si négation détectée
                positive_score, negative_score = negative_score, positive_score
            
            # Normalisation des scores
            total_score = positive_score + negative_score + neutral_score
            if total_score > 0:
                positive_score /= total_score
                negative_score /= total_score
                neutral_score /= total_score
            
            # Détermination du sentiment principal
            if positive_score > negative_score and positive_score > neutral_score:
                label = "positive"
                score = positive_score
            elif negative_score > positive_score and negative_score > neutral_score:
                label = "negative"
                score = -negative_score  # Score négatif
            else:
                label = "neutral"
                score = 0.0
            
            # Détection de l'urgence
            urgency = self._detect_urgency(message_lower, label, score)
            
            return {
                "label": label,
                "score": score,
                "confidence": max(positive_score, negative_score, neutral_score),
                "urgency": urgency,
                "emotions": self._detect_emotions(message_lower),
                "keywords_found": self._extract_sentiment_keywords(message_lower)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sentiment: {e}")
            return {
                "label": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "urgency": "low",
                "emotions": [],
                "keywords_found": []
            }
    
    def _calculate_sentiment_score(self, message: str, patterns: Dict[str, Any]) -> float:
        """Calcule le score de sentiment basé sur les patterns"""
        score = 0.0
        
        # Score des mots-clés
        keywords = patterns.get("keywords", [])
        for keyword in keywords:
            if keyword in message:
                # Score pondéré selon la longueur du mot
                score += 1.0 / len(keyword.split())
        
        # Score des emojis
        emojis = patterns.get("emojis", [])
        for emoji in emojis:
            if emoji in message:
                score += 2.0  # Emojis ont plus de poids
        
        # Score des patterns regex
        regex_patterns = patterns.get("patterns", [])
        for pattern in regex_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                score += 3.0  # Patterns ont le plus de poids
        
        return score
    
    def _apply_modifiers(self, message: str, score: float, sentiment_type: str) -> float:
        """Applique les modificateurs d'intensité"""
        intensifiers = self.intensifiers.get(sentiment_type, [])
        
        for intensifier in intensifiers:
            if intensifier in message:
                score *= 1.5  # Augmentation de 50% pour les intensificateurs
        
        # Détection de la répétition (ex: "très très bien")
        repetition_pattern = r"(\w+)\s+\1"
        repetitions = len(re.findall(repetition_pattern, message))
        if repetitions > 0:
            score *= (1 + repetitions * 0.3)  # Augmentation pour les répétitions
        
        return score
    
    def _has_negation(self, message: str) -> bool:
        """Détecte la présence de négations"""
        for negation in self.negations:
            if negation in message:
                return True
        return False
    
    def _detect_urgency(self, message: str, label: str, score: float) -> str:
        """Détecte le niveau d'urgence du message"""
        urgency_keywords = [
            "urgent", "urgence", "immédiat", "tout de suite", "rapidement",
            "vite", "dépêche", "pressé", "critique", "grave", "important"
        ]
        
        # Mots-clés d'urgence
        urgency_count = sum(1 for keyword in urgency_keywords if keyword in message)
        
        # Majuscules (cri)
        caps_ratio = sum(1 for c in message if c.isupper()) / len(message) if message else 0
        
        # Points d'exclamation
        exclamation_count = message.count('!')
        
        # Calcul du score d'urgence
        urgency_score = urgency_count * 2 + caps_ratio * 10 + exclamation_count * 0.5
        
        # Sentiment négatif intense
        if label == "negative" and abs(score) > 0.7:
            urgency_score += 3
        
        # Classification de l'urgence
        if urgency_score >= 5:
            return "high"
        elif urgency_score >= 2:
            return "medium"
        else:
            return "low"
    
    def _detect_emotions(self, message: str) -> List[str]:
        """Détecte les émotions spécifiques dans le message"""
        emotions = []
        
        emotion_patterns = {
            "frustration": ["frustré", "énervé", "agacé", "exaspéré", "irrité"],
            "colère": ["fâché", "en colère", "furieux", "rage", "indigné"],
            "tristesse": ["triste", "déprimé", "déçu", "désolé", "malheureux"],
            "joie": ["heureux", "content", "joyeux", "gai", "enthousiaste"],
            "surprise": ["surpris", "étonné", "choqué", "stupéfait", "incroyable"],
            "peur": ["inquiet", "anxieux", "stressé", "paniqué", "terrifié"],
            "confusion": ["confus", "perdu", "perplexe", "désorienté", "embrouillé"]
        }
        
        for emotion, keywords in emotion_patterns.items():
            if any(keyword in message for keyword in keywords):
                emotions.append(emotion)
        
        return emotions
    
    def _extract_sentiment_keywords(self, message: str) -> List[str]:
        """Extrait les mots-clés de sentiment trouvés"""
        all_keywords = (
            self.positive_patterns["keywords"] + 
            self.negative_patterns["keywords"] + 
            self.neutral_patterns["keywords"]
        )
        
        found_keywords = [keyword for keyword in all_keywords if keyword in message]
        return found_keywords
    
    def get_sentiment_examples(self, sentiment: str) -> List[str]:
        """Retourne des exemples de messages pour un sentiment"""
        examples = {
            "positive": [
                "Merci beaucoup pour votre aide !",
                "Service parfait, je suis très satisfait",
                "Excellent travail, bravo !",
                "Je recommande vivement Free Mobile"
            ],
            "negative": [
                "C'est nul, ça ne marche pas du tout",
                "Je suis très déçu de ce service",
                "Horrible, je vais changer d'opérateur",
                "C'est une catastrophe, je suis furieux"
            ],
            "neutral": [
                "J'ai une question sur mon forfait",
                "Pouvez-vous m'aider ?",
                "Je voudrais des informations",
                "Comment faire pour..."
            ]
        }
        
        return examples.get(sentiment, [])
    
    def get_sentiment_stats(self, messages: List[str]) -> Dict[str, Any]:
        """Calcule les statistiques de sentiment pour une liste de messages"""
        sentiments = [self.analyze_sentiment(msg) for msg in messages]
        
        total = len(sentiments)
        if total == 0:
            return {"total": 0, "positive": 0, "negative": 0, "neutral": 0}
        
        positive_count = sum(1 for s in sentiments if s["label"] == "positive")
        negative_count = sum(1 for s in sentiments if s["label"] == "negative")
        neutral_count = sum(1 for s in sentiments if s["label"] == "neutral")
        
        avg_score = sum(s["score"] for s in sentiments) / total
        high_urgency = sum(1 for s in sentiments if s["urgency"] == "high")
        
        return {
            "total": total,
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "positive_rate": positive_count / total,
            "negative_rate": negative_count / total,
            "neutral_rate": neutral_count / total,
            "average_score": avg_score,
            "high_urgency_rate": high_urgency / total
        }


