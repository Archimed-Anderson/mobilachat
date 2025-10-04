"""
Version simplifiée du Vector Store sans ChromaDB
Utilise des embeddings en mémoire pour le développement
"""
import json
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config.settings import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector Store simplifié utilisant des embeddings en mémoire"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.embedding_model = None
        self.documents = []
        self.embeddings = []
        self.metadata = []
        self._initialize()
        
    def _initialize(self):
        """Initialise le modèle d'embedding"""
        try:
            logger.info(f"Chargement du modèle d'embedding: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info("Modèle d'embedding chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Ajoute des documents au store"""
        try:
            if not documents:
                logger.warning("Aucun document à ajouter")
                return False
            
            # Extraction des textes et métadonnées
            texts = [doc["content"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            # Génération des embeddings
            logger.info(f"Génération des embeddings pour {len(texts)} documents...")
            embeddings = self.embedding_model.encode(texts)
            
            # Ajout au store
            self.documents.extend(texts)
            self.embeddings.extend(embeddings)
            self.metadata.extend(metadatas)
            
            logger.info(f"{len(documents)} documents ajoutés avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {e}")
            return False
    
    def search(
        self, 
        query: str, 
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Recherche de similarité"""
        try:
            if not self.embedding_model or not self.documents:
                return []
            
            if top_k is None:
                top_k = settings.RAG_TOP_K
            
            # Embedding de la requête
            query_embedding = self.embedding_model.encode([query])
            
            # Calcul des similarités
            similarities = np.dot(query_embedding, np.array(self.embeddings).T)[0]
            
            # Tri par similarité
            indices = np.argsort(similarities)[::-1]
            
            results = []
            for idx in indices[:top_k]:
                similarity = float(similarities[idx])
                if similarity >= settings.RAG_SIMILARITY_THRESHOLD:
                    # Filtrage par métadonnées si spécifié
                    if filter_metadata:
                        doc_metadata = self.metadata[idx]
                        if not all(doc_metadata.get(k) == v for k, v in filter_metadata.items()):
                            continue
                    
                    results.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "distance": 1 - similarity,
                        "similarity": similarity
                    })
            
            logger.info(f"Recherche terminée: {len(results)} documents trouvés")
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du store"""
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0,
            "model_name": self.model_name,
            "collection_name": settings.VECTOR_STORE_COLLECTION,
            "similarity_threshold": settings.RAG_SIMILARITY_THRESHOLD
        }
    
    def reset_collection(self) -> bool:
        """Vide le store"""
        try:
            self.documents = []
            self.embeddings = []
            self.metadata = []
            logger.info("Collection réinitialisée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation: {e}")
            return False
    
    def get_relevant_context(
        self, 
        query: str, 
        context_type: Optional[str] = None
    ) -> str:
        """Récupère le contexte pertinent pour une requête"""
        try:
            # Filtrage par type de contexte si spécifié
            filter_metadata = None
            if context_type:
                filter_metadata = {"type": context_type}
            
            # Recherche des documents pertinents
            relevant_docs = self.search(query, filter_metadata=filter_metadata)
            
            if not relevant_docs:
                return ""
            
            # Construction du contexte
            context_parts = []
            for doc in relevant_docs:
                title = doc['metadata'].get('title', 'Document')
                content = doc['content']
                context_parts.append(f"**{title}**\n{content}")
            
            context = "\n\n".join(context_parts)
            
            # Limitation de la longueur du contexte
            max_length = getattr(settings, 'MAX_CONTEXT_LENGTH', 2000)
            if len(context) > max_length:
                context = context[:max_length] + "..."
            
            return context
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contexte: {e}")
            return ""


# Instance globale
vector_store = VectorStore()