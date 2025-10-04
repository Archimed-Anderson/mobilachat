"""
Générateur de réponses IA avec RAG
"""
import logging
from typing import Dict, Any, List, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from ..config.settings import settings
from ..rag.vector_store import vector_store
from .intent_detector import IntentDetector
from .sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)


class ResponseGenerator:
    def __init__(self):
        self.llm_pipeline = None
        self.tokenizer = None
        self.intent_detector = IntentDetector()
        self.sentiment_analyzer = SentimentAnalyzer()
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialise le modèle de génération de texte"""
        try:
            logger.info(f"Chargement du modèle LLM: {settings.LLM_MODEL_NAME}")
            
            # Configuration du device
            device = 0 if settings.LLM_DEVICE == "cuda" and torch.cuda.is_available() else -1
            
            # Chargement du tokenizer et du modèle
            self.tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL_NAME)
            model = AutoModelForCausalLM.from_pretrained(
                settings.LLM_MODEL_NAME,
                torch_dtype=torch.float16 if device == 0 else torch.float32
            )
            
            # Configuration du tokenizer
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Création du pipeline
            self.llm_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=self.tokenizer,
                device=device,
                max_length=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            logger.info("Modèle LLM initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du modèle: {e}")
            # Fallback vers un modèle plus simple
            self._initialize_fallback_model()
    
    def _initialize_fallback_model(self):
        """Initialise un modèle de fallback plus simple"""
        try:
            logger.info("Initialisation du modèle de fallback...")
            self.llm_pipeline = pipeline(
                "text-generation",
                model="gpt2",
                device=-1,
                max_length=256,
                temperature=0.7
            )
            logger.info("Modèle de fallback initialisé")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du fallback: {e}")
            self.llm_pipeline = None
    
    def generate_response(
        self, 
        message: str, 
        conversation_id: str,
        context_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère une réponse IA basée sur le message et le contexte"""
        try:
            # Détection de l'intention
            intent = self.intent_detector.detect_intent(message)
            
            # Analyse du sentiment
            sentiment = self.sentiment_analyzer.analyze_sentiment(message)
            
            # Récupération du contexte pertinent
            context = vector_store.get_relevant_context(message, intent.get("category"))
            
            # Construction du prompt
            prompt = self._build_prompt(message, context, intent, sentiment)
            
            # Génération de la réponse
            if self.llm_pipeline:
                response_text = self._generate_text(prompt)
            else:
                response_text = self._generate_fallback_response(intent, sentiment)
            
            # Vérification de l'escalade
            needs_escalation = self._check_escalation_needed(message, intent, sentiment)
            
            # Génération des liens suggérés
            suggested_links = self._generate_suggested_links(intent, sentiment)
            
            return {
                "response": response_text,
                "intent": intent,
                "sentiment": sentiment,
                "needs_escalation": needs_escalation,
                "suggested_links": suggested_links,
                "context_used": bool(context)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse: {e}")
            return {
                "response": "Désolé, je rencontre un problème technique. Veuillez réessayer plus tard.",
                "intent": {"category": "error", "confidence": 0.0},
                "sentiment": {"label": "neutral", "score": 0.0},
                "needs_escalation": True,
                "suggested_links": [],
                "context_used": False
            }
    
    def _build_prompt(
        self, 
        message: str, 
        context: str, 
        intent: Dict[str, Any], 
        sentiment: Dict[str, Any]
    ) -> str:
        """Construit le prompt pour le modèle IA"""
        
        # Instructions de base
        system_prompt = """Vous êtes un assistant virtuel spécialisé dans le support client Free Mobile. 
Votre rôle est d'aider les clients avec leurs questions sur les forfaits, la facturation, les problèmes techniques, etc.

Instructions importantes:
- Répondez toujours en français
- Soyez professionnel, courtois et empathique
- Utilisez les informations de contexte fournies
- Si vous ne savez pas, proposez des liens utiles
- Pour les problèmes complexes, proposez l'escalade vers un agent humain
- Restez concis mais informatif"""

        # Contexte spécifique selon l'intention
        context_prompt = ""
        if context:
            context_prompt = f"\n\nContexte pertinent:\n{context}"
        
        # Instructions selon l'intention détectée
        intent_instructions = self._get_intent_instructions(intent)
        
        # Instructions selon le sentiment
        sentiment_instructions = self._get_sentiment_instructions(sentiment)
        
        # Construction du prompt final
        prompt = f"""{system_prompt}

{intent_instructions}
{sentiment_instructions}

Message du client: {message}
{context_prompt}

Réponse:"""
        
        return prompt
    
    def _get_intent_instructions(self, intent: Dict[str, Any]) -> str:
        """Retourne les instructions spécifiques selon l'intention"""
        category = intent.get("category", "general")
        
        instructions = {
            "facturation": "Le client a une question sur la facturation. Vérifiez les informations de facturation et proposez des solutions.",
            "technique": "Le client a un problème technique. Proposez des solutions de dépannage étape par étape.",
            "forfait": "Le client s'interroge sur les forfaits. Présentez les options disponibles et leurs avantages.",
            "resiliation": "Le client souhaite résilier. Expliquez la procédure et proposez des alternatives.",
            "general": "Répondez de manière générale en proposant de l'aide."
        }
        
        return instructions.get(category, instructions["general"])
    
    def _get_sentiment_instructions(self, sentiment: Dict[str, Any]) -> str:
        """Retourne les instructions selon le sentiment"""
        label = sentiment.get("label", "neutral")
        
        if label == "negative":
            return "Le client semble mécontent. Soyez particulièrement empathique et proposez des solutions concrètes."
        elif label == "positive":
            return "Le client semble satisfait. Maintenez cette satisfaction et proposez une aide supplémentaire."
        else:
            return "Répondez de manière neutre et professionnelle."
    
    def _generate_text(self, prompt: str) -> str:
        """Génère du texte avec le modèle IA"""
        try:
            # Génération avec le pipeline
            outputs = self.llm_pipeline(
                prompt,
                max_new_tokens=200,
                temperature=settings.LLM_TEMPERATURE,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            # Extraction de la réponse
            generated_text = outputs[0]["generated_text"]
            response = generated_text[len(prompt):].strip()
            
            # Nettoyage de la réponse
            response = self._clean_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de texte: {e}")
            return self._generate_fallback_response({}, {})
    
    def _clean_response(self, response: str) -> str:
        """Nettoie la réponse générée"""
        # Suppression des répétitions
        lines = response.split('\n')
        cleaned_lines = []
        seen = set()
        
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                cleaned_lines.append(line)
                seen.add(line)
        
        response = '\n'.join(cleaned_lines)
        
        # Limitation de la longueur
        if len(response) > 500:
            response = response[:500] + "..."
        
        return response
    
    def _generate_fallback_response(
        self, 
        intent: Dict[str, Any], 
        sentiment: Dict[str, Any]
    ) -> str:
        """Génère une réponse de fallback"""
        category = intent.get("category", "general")
        
        responses = {
            "facturation": "Pour toute question de facturation, je vous invite à consulter votre espace client Free Mobile ou à contacter notre service client.",
            "technique": "Pour résoudre votre problème technique, je vous recommande de redémarrer votre appareil et de vérifier les paramètres réseau.",
            "forfait": "Je peux vous aider à choisir le forfait qui vous convient le mieux. Consultez notre site web pour voir toutes les options disponibles.",
            "resiliation": "Si vous souhaitez résilier votre contrat, vous pouvez le faire depuis votre espace client ou en contactant notre service client.",
            "general": "Je suis là pour vous aider. Pouvez-vous me donner plus de détails sur votre demande ?"
        }
        
        base_response = responses.get(category, responses["general"])
        
        if sentiment.get("label") == "negative":
            base_response = "Je comprends votre frustration. " + base_response
        
        return base_response
    
    def _check_escalation_needed(
        self, 
        message: str, 
        intent: Dict[str, Any], 
        sentiment: Dict[str, Any]
    ) -> bool:
        """Vérifie si une escalade est nécessaire"""
        # Mots-clés d'escalade
        escalation_keywords = [
            "rémunération", "plainte", "réclamation", "juridique", "avocat",
            "médiateur", "ARCEP", "résiliation immédiate", "dédommagement"
        ]
        
        message_lower = message.lower()
        
        # Vérification des mots-clés
        for keyword in escalation_keywords:
            if keyword in message_lower:
                return True
        
        # Vérification du sentiment très négatif
        if sentiment.get("score", 0) < -0.7:
            return True
        
        # Vérification de l'intention complexe
        if intent.get("category") in ["resiliation", "technique"] and intent.get("confidence", 0) < 0.5:
            return True
        
        return False
    
    def _generate_suggested_links(
        self, 
        intent: Dict[str, Any], 
        sentiment: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Génère des liens suggérés selon l'intention"""
        category = intent.get("category", "general")
        
        links = {
            "facturation": [
                {
                    "title": "Espace Client",
                    "url": settings.FREE_MOBILE_ESPACE_CLIENT_URL,
                    "description": "Consultez vos factures et votre consommation"
                },
                {
                    "title": "FAQ Facturation",
                    "url": f"{settings.FREE_MOBILE_FAQ_URL}#facturation",
                    "description": "Questions fréquentes sur la facturation"
                }
            ],
            "technique": [
                {
                    "title": "Guide de Dépannage",
                    "url": f"{settings.FREE_MOBILE_FAQ_URL}#technique",
                    "description": "Solutions aux problèmes techniques courants"
                },
                {
                    "title": "Contact Support",
                    "url": settings.FREE_MOBILE_CONTACT_URL,
                    "description": "Contacter notre équipe technique"
                }
            ],
            "forfait": [
                {
                    "title": "Nos Forfaits",
                    "url": "https://mobile.free.fr/offres/",
                    "description": "Découvrez tous nos forfaits mobiles"
                },
                {
                    "title": "Comparateur",
                    "url": "https://mobile.free.fr/offres/comparateur",
                    "description": "Comparez nos offres"
                }
            ],
            "resiliation": [
                {
                    "title": "Procédure de Résiliation",
                    "url": f"{settings.FREE_MOBILE_FAQ_URL}#resiliation",
                    "description": "Comment résilier votre contrat"
                },
                {
                    "title": "Espace Client",
                    "url": settings.FREE_MOBILE_ESPACE_CLIENT_URL,
                    "description": "Résiliez en ligne"
                }
            ]
        }
        
        return links.get(category, [
            {
                "title": "FAQ Générale",
                "url": settings.FREE_MOBILE_FAQ_URL,
                "description": "Trouvez des réponses à vos questions"
            },
            {
                "title": "Contact",
                "url": settings.FREE_MOBILE_CONTACT_URL,
                "description": "Contacter notre service client"
            }
        ])


