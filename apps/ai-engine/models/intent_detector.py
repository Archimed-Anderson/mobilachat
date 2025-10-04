"""
Détecteur d'intention pour classifier les messages
"""
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class IntentDetector:
    def __init__(self):
        # Patterns de mots-clés pour chaque intention
        self.intent_patterns = {
            "facturation": {
                "keywords": [
                    "facture", "facturation", "paiement", "prélèvement", "débit",
                    "coût", "prix", "tarif", "montant", "euros", "€", "billing",
                    "consommation", "dépassement", "forfait", "data", "go", "mo",
                    "sms", "appel", "minute", "internet", "4g", "5g"
                ],
                "patterns": [
                    r"combien.*coût",
                    r"prix.*forfait",
                    r"facture.*montant",
                    r"dépassement.*data",
                    r"consommation.*internet"
                ]
            },
            "technique": {
                "keywords": [
                    "problème", "bug", "erreur", "ne marche pas", "fonctionne pas",
                    "connexion", "réseau", "signal", "4g", "5g", "wifi", "bluetooth",
                    "appareil", "téléphone", "smartphone", "sim", "carte sim",
                    "dépannage", "redémarrage", "reset", "paramètres", "configuration"
                ],
                "patterns": [
                    r"ne.*fonctionne.*pas",
                    r"problème.*connexion",
                    r"erreur.*réseau",
                    r"signal.*faible",
                    r"wifi.*marche.*pas"
                ]
            },
            "forfait": {
                "keywords": [
                    "forfait", "offre", "tarif", "abonnement", "souscription",
                    "changer", "modifier", "upgrade", "downgrade", "migration",
                    "nouveau", "nouvelle", "offre", "promo", "réduction",
                    "illimité", "data", "sms", "appels", "internet"
                ],
                "patterns": [
                    r"changer.*forfait",
                    r"nouveau.*forfait",
                    r"offre.*disponible",
                    r"migration.*forfait",
                    r"tarif.*forfait"
                ]
            },
            "resiliation": {
                "keywords": [
                    "résilier", "résiliation", "annuler", "arrêter", "stopper",
                    "quitter", "partir", "changer", "opérateur", "concurrent",
                    "départ", "fin", "terminer", "clôturer", "fermer"
                ],
                "patterns": [
                    r"résilier.*contrat",
                    r"arrêter.*forfait",
                    r"changer.*opérateur",
                    r"partir.*free",
                    r"annuler.*abonnement"
                ]
            },
            "livraison": {
                "keywords": [
                    "livraison", "livrer", "expédition", "colis", "commande",
                    "suivi", "tracking", "réception", "reçu", "arrivé",
                    "retard", "en retard", "perdu", "volé", "vol"
                ],
                "patterns": [
                    r"livraison.*commande",
                    r"suivi.*colis",
                    r"retard.*livraison",
                    r"colis.*perdu"
                ]
            },
            "commande": {
                "keywords": [
                    "commander", "commande", "achat", "acheter", "souscrire",
                    "souscription", "nouveau", "nouvelle", "sim", "carte",
                    "téléphone", "smartphone", "appareil", "équipement"
                ],
                "patterns": [
                    r"commander.*forfait",
                    r"nouveau.*abonnement",
                    r"souscrire.*offre",
                    r"acheter.*sim"
                ]
            }
        }
        
        # Intentions par défaut
        self.default_intent = "general"
    
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """Détecte l'intention d'un message"""
        try:
            message_lower = message.lower()
            
            # Calcul des scores pour chaque intention
            intent_scores = {}
            
            for intent, config in self.intent_patterns.items():
                score = self._calculate_intent_score(message_lower, config)
                intent_scores[intent] = score
            
            # Sélection de l'intention avec le score le plus élevé
            best_intent = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent]
            
            # Seuil de confiance minimum
            confidence_threshold = 0.3
            
            if best_score < confidence_threshold:
                best_intent = self.default_intent
                best_score = 0.5  # Score neutre pour l'intention générale
            
            # Détection de sous-catégories
            subcategory = self._detect_subcategory(message_lower, best_intent)
            
            return {
                "category": best_intent,
                "subcategory": subcategory,
                "confidence": min(best_score, 1.0),
                "keywords_found": self._extract_found_keywords(message_lower, best_intent)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'intention: {e}")
            return {
                "category": self.default_intent,
                "subcategory": None,
                "confidence": 0.0,
                "keywords_found": []
            }
    
    def _calculate_intent_score(self, message: str, config: Dict[str, Any]) -> float:
        """Calcule le score d'intention basé sur les mots-clés et patterns"""
        score = 0.0
        
        # Score des mots-clés
        keywords = config.get("keywords", [])
        keyword_matches = 0
        
        for keyword in keywords:
            if keyword in message:
                keyword_matches += 1
                # Score pondéré selon la longueur du mot-clé
                score += 1.0 / len(keyword.split())
        
        # Normalisation par le nombre de mots-clés
        if keywords:
            keyword_score = (keyword_matches / len(keywords)) * 0.7
        else:
            keyword_score = 0.0
        
        # Score des patterns regex
        patterns = config.get("patterns", [])
        pattern_matches = 0
        
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                pattern_matches += 1
                score += 2.0  # Patterns ont plus de poids
        
        # Normalisation par le nombre de patterns
        if patterns:
            pattern_score = (pattern_matches / len(patterns)) * 0.3
        else:
            pattern_score = 0.0
        
        # Score final
        final_score = keyword_score + pattern_score
        
        # Bonus pour les messages courts avec beaucoup de mots-clés
        if len(message.split()) < 10 and keyword_matches > 0:
            final_score *= 1.2
        
        return min(final_score, 1.0)
    
    def _detect_subcategory(self, message: str, intent: str) -> str:
        """Détecte la sous-catégorie d'une intention"""
        subcategories = {
            "facturation": {
                "data": ["data", "internet", "4g", "5g", "go", "mo", "dépassement"],
                "appels": ["appel", "minute", "sms", "mms", "communication"],
                "facture": ["facture", "prélèvement", "paiement", "montant"]
            },
            "technique": {
                "connexion": ["connexion", "réseau", "signal", "4g", "5g"],
                "appareil": ["téléphone", "smartphone", "appareil", "sim"],
                "wifi": ["wifi", "wifi", "bluetooth", "paramètres"]
            },
            "forfait": {
                "data": ["data", "internet", "illimité", "limité"],
                "communication": ["appels", "sms", "illimité", "limité"],
                "prix": ["prix", "tarif", "coût", "euros", "€"]
            }
        }
        
        if intent not in subcategories:
            return None
        
        intent_subcats = subcategories[intent]
        best_subcat = None
        best_score = 0
        
        for subcat, keywords in intent_subcats.items():
            score = sum(1 for keyword in keywords if keyword in message)
            if score > best_score:
                best_score = score
                best_subcat = subcat
        
        return best_subcat if best_score > 0 else None
    
    def _extract_found_keywords(self, message: str, intent: str) -> List[str]:
        """Extrait les mots-clés trouvés dans le message"""
        if intent not in self.intent_patterns:
            return []
        
        keywords = self.intent_patterns[intent].get("keywords", [])
        found_keywords = [keyword for keyword in keywords if keyword in message]
        
        return found_keywords
    
    def get_intent_examples(self, intent: str) -> List[str]:
        """Retourne des exemples de messages pour une intention"""
        examples = {
            "facturation": [
                "Combien coûte mon forfait ?",
                "Je ne comprends pas ma facture",
                "J'ai dépassé mon forfait data",
                "Quel est le prix des appels internationaux ?"
            ],
            "technique": [
                "Mon téléphone ne se connecte pas à internet",
                "Je n'ai pas de signal 4G",
                "Le WiFi ne fonctionne pas",
                "Mon appareil ne démarre plus"
            ],
            "forfait": [
                "Je veux changer de forfait",
                "Quelles sont vos offres ?",
                "Pouvez-vous me proposer un forfait moins cher ?",
                "Je veux plus de data"
            ],
            "resiliation": [
                "Je veux résilier mon contrat",
                "Comment arrêter mon abonnement ?",
                "Je change d'opérateur",
                "Je veux quitter Free Mobile"
            ]
        }
        
        return examples.get(intent, [])
    
    def get_supported_intents(self) -> List[str]:
        """Retourne la liste des intentions supportées"""
        return list(self.intent_patterns.keys()) + [self.default_intent]


