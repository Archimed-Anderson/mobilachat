"""
Processeur de documents pour le RAG
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from PyPDF2 import PdfReader
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self, data_path: str = "./data"):
        self.data_path = Path(data_path)
        self.supported_formats = {".json", ".pdf", ".md", ".txt"}
    
    def process_all_documents(self) -> List[Dict[str, Any]]:
        """Traite tous les documents dans le dossier data"""
        documents = []
        
        # Traitement des FAQs JSON
        faq_docs = self._process_faqs()
        documents.extend(faq_docs)
        
        # Traitement des documents PDF
        pdf_docs = self._process_pdfs()
        documents.extend(pdf_docs)
        
        # Traitement des documents Markdown
        md_docs = self._process_markdown()
        documents.extend(md_docs)
        
        logger.info(f"Total de {len(documents)} documents traités")
        return documents
    
    def _process_faqs(self) -> List[Dict[str, Any]]:
        """Traite les fichiers FAQ JSON"""
        documents = []
        faq_path = self.data_path / "raw" / "faqs"
        
        if not faq_path.exists():
            logger.warning(f"Dossier FAQs non trouvé: {faq_path}")
            return documents
        
        for json_file in faq_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    faq_data = json.load(f)
                
                # Traitement des FAQs
                for category, faqs in faq_data.items():
                    for i, faq in enumerate(faqs):
                        doc = {
                            "id": f"faq_{category}_{i}",
                            "content": f"Q: {faq['question']}\nR: {faq['answer']}",
                            "metadata": {
                                "type": "faq",
                                "category": category,
                                "source": json_file.name,
                                "title": faq['question'][:100] + "..." if len(faq['question']) > 100 else faq['question']
                            }
                        }
                        documents.append(doc)
                
                logger.info(f"FAQs traitées: {json_file.name}")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {json_file}: {e}")
        
        return documents
    
    def _process_pdfs(self) -> List[Dict[str, Any]]:
        """Traite les fichiers PDF"""
        documents = []
        pdf_path = self.data_path / "raw" / "documentation"
        
        if not pdf_path.exists():
            logger.warning(f"Dossier documentation non trouvé: {pdf_path}")
            return documents
        
        for pdf_file in pdf_path.glob("*.pdf"):
            try:
                reader = PdfReader(pdf_file)
                content = ""
                
                for page in reader.pages:
                    content += page.extract_text() + "\n"
                
                if content.strip():
                    # Découpage en chunks
                    chunks = self._split_text(content, chunk_size=1000, overlap=200)
                    
                    for i, chunk in enumerate(chunks):
                        doc = {
                            "id": f"pdf_{pdf_file.stem}_{i}",
                            "content": chunk,
                            "metadata": {
                                "type": "documentation",
                                "source": pdf_file.name,
                                "title": f"{pdf_file.stem} - Partie {i+1}",
                                "chunk_index": i
                            }
                        }
                        documents.append(doc)
                
                logger.info(f"PDF traité: {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {pdf_file}: {e}")
        
        return documents
    
    def _process_markdown(self) -> List[Dict[str, Any]]:
        """Traite les fichiers Markdown"""
        documents = []
        md_path = self.data_path / "raw" / "documentation"
        
        if not md_path.exists():
            logger.warning(f"Dossier documentation non trouvé: {md_path}")
            return documents
        
        for md_file in md_path.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Conversion Markdown vers HTML puis texte
                html = markdown.markdown(content)
                soup = BeautifulSoup(html, 'html.parser')
                text_content = soup.get_text()
                
                if text_content.strip():
                    # Découpage en chunks
                    chunks = self._split_text(text_content, chunk_size=1000, overlap=200)
                    
                    for i, chunk in enumerate(chunks):
                        doc = {
                            "id": f"md_{md_file.stem}_{i}",
                            "content": chunk,
                            "metadata": {
                                "type": "documentation",
                                "source": md_file.name,
                                "title": f"{md_file.stem} - Partie {i+1}",
                                "chunk_index": i
                            }
                        }
                        documents.append(doc)
                
                logger.info(f"Markdown traité: {md_file.name}")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {md_file}: {e}")
        
        return documents
    
    def _split_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        overlap: int = 200
    ) -> List[str]:
        """Découpe un texte en chunks avec overlap"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Essayer de couper à la fin d'une phrase
            if end < len(text):
                # Chercher le dernier point, point d'exclamation ou point d'interrogation
                last_sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if last_sentence_end > start + chunk_size // 2:
                    end = last_sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def process_conversations(self) -> List[Dict[str, Any]]:
        """Traite les conversations d'entraînement"""
        documents = []
        conv_path = self.data_path / "raw" / "conversations"
        
        if not conv_path.exists():
            logger.warning(f"Dossier conversations non trouvé: {conv_path}")
            return documents
        
        for json_file in conv_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    conversations = json.load(f)
                
                for i, conv in enumerate(conversations):
                    # Construction du contenu de la conversation
                    content_parts = []
                    for message in conv.get("messages", []):
                        role = message.get("role", "user")
                        content = message.get("content", "")
                        content_parts.append(f"{role}: {content}")
                    
                    content = "\n".join(content_parts)
                    
                    if content.strip():
                        doc = {
                            "id": f"conv_{json_file.stem}_{i}",
                            "content": content,
                            "metadata": {
                                "type": "conversation",
                                "source": json_file.name,
                                "title": f"Conversation {i+1}",
                                "intent": conv.get("intent", "unknown"),
                                "category": conv.get("category", "general")
                            }
                        }
                        documents.append(doc)
                
                logger.info(f"Conversations traitées: {json_file.name}")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {json_file}: {e}")
        
        return documents


