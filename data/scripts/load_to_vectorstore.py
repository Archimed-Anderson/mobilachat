#!/usr/bin/env python3
"""
Script de chargement des données dans ChromaDB
"""
import sys
import os
from pathlib import Path

# Ajout du chemin du projet
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from apps.ai_engine.rag.document_processor import DocumentProcessor
from apps.ai_engine.rag.vector_store import vector_store
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale"""
    print("🔄 Chargement des données dans ChromaDB...")
    
    # Initialisation du processeur de documents
    processor = DocumentProcessor()
    
    # Option de réinitialisation
    reset = input("Voulez-vous réinitialiser la collection ? (y/N): ").lower() == 'y'
    
    if reset:
        print("🗑️ Réinitialisation de la collection...")
        vector_store.reset_collection()
        print("✅ Collection réinitialisée")
    
    # Traitement des documents
    print("📚 Traitement des documents...")
    documents = processor.process_all_documents()
    
    if not documents:
        print("❌ Aucun document trouvé")
        return
    
    print(f"✅ {len(documents)} documents traités")
    
    # Ajout au vector store
    print("💾 Ajout au vector store...")
    success = vector_store.add_documents(documents)
    
    if success:
        print("✅ Documents ajoutés avec succès")
    else:
        print("❌ Erreur lors de l'ajout des documents")
        return
    
    # Statistiques
    stats = vector_store.get_stats()
    print(f"\n📊 Statistiques:")
    print(f"  Documents dans la collection: {stats.get('total_documents', 0)}")
    print(f"  Modèle d'embedding: {stats.get('embedding_model', 'N/A')}")
    print(f"  Seuil de similarité: {stats.get('similarity_threshold', 'N/A')}")
    
    # Test de recherche
    print("\n🔍 Test de recherche...")
    test_queries = [
        "Comment consulter ma facture ?",
        "Mon téléphone ne capte pas la 4G",
        "Je veux changer de forfait",
        "Comment résilier mon contrat ?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = vector_store.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['metadata'].get('title', 'Sans titre')}")
            print(f"     Similarité: {result['similarity']:.3f}")
            print(f"     Contenu: {result['content'][:100]}...")
    
    print("\n✅ Chargement terminé !")


if __name__ == "__main__":
    main()


