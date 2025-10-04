#!/usr/bin/env python3
"""
Script de préparation des datasets pour l'entraînement
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import random


def load_faqs(data_path: Path) -> List[Dict[str, Any]]:
    """Charge les FAQs depuis les fichiers JSON"""
    faqs = []
    faq_path = data_path / "raw" / "faqs"
    
    for json_file in faq_path.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for category, faq_list in data.items():
            for faq in faq_list:
                faqs.append({
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": category,
                    "source": json_file.name
                })
    
    return faqs


def create_training_variations(faqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Crée des variations des FAQs pour l'entraînement"""
    variations = []
    
    for faq in faqs:
        # Version originale
        variations.append({
            "input": faq["question"],
            "output": faq["answer"],
            "category": faq["category"],
            "type": "original"
        })
        
        # Variations de formulation
        variations.extend(create_question_variations(faq))
        
        # Variations de réponse
        variations.extend(create_answer_variations(faq))
    
    return variations


def create_question_variations(faq: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Crée des variations de questions"""
    variations = []
    question = faq["question"]
    answer = faq["answer"]
    category = faq["category"]
    
    # Variations de politesse
    polite_variations = [
        f"Bonjour, {question.lower()}",
        f"Salut, {question.lower()}",
        f"Excusez-moi, {question.lower()}",
        f"Pouvez-vous me dire {question.lower()} ?"
    ]
    
    for variation in polite_variations:
        variations.append({
            "input": variation,
            "output": answer,
            "category": category,
            "type": "polite_variation"
        })
    
    # Variations de contexte
    context_variations = [
        f"J'ai un problème : {question.lower()}",
        f"Je ne comprends pas : {question.lower()}",
        f"J'aimerais savoir {question.lower()}",
        f"Comment faire pour {question.lower().replace('?', '')} ?"
    ]
    
    for variation in context_variations:
        variations.append({
            "input": variation,
            "output": answer,
            "category": category,
            "type": "context_variation"
        })
    
    return variations


def create_answer_variations(faq: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Crée des variations de réponses"""
    variations = []
    question = faq["question"]
    answer = faq["answer"]
    category = faq["category"]
    
    # Réponses courtes
    short_answer = answer.split('.')[0] + "."
    variations.append({
        "input": question,
        "output": short_answer,
        "category": category,
        "type": "short_answer"
    })
    
    # Réponses avec contexte
    contextual_answer = f"Pour répondre à votre question sur {category} : {answer}"
    variations.append({
        "input": question,
        "output": contextual_answer,
        "category": category,
        "type": "contextual_answer"
    })
    
    return variations


def create_conversation_examples() -> List[Dict[str, Any]]:
    """Crée des exemples de conversations"""
    conversations = []
    
    # Conversation facturation
    conversations.append({
        "messages": [
            {"role": "user", "content": "Bonjour, je ne comprends pas ma facture"},
            {"role": "assistant", "content": "Bonjour ! Je peux vous aider à comprendre votre facture. Pouvez-vous me dire ce qui vous pose problème exactement ?"},
            {"role": "user", "content": "Il y a des frais supplémentaires que je ne comprends pas"},
            {"role": "assistant", "content": "Les frais supplémentaires peuvent être liés à un dépassement de votre forfait. Vérifiez votre consommation dans votre espace client. Si vous avez dépassé votre forfait data, des frais de 0,05€ par Mo s'appliquent."}
        ],
        "intent": "facturation",
        "category": "facturation",
        "sentiment": "neutral"
    })
    
    # Conversation technique
    conversations.append({
        "messages": [
            {"role": "user", "content": "Mon téléphone ne capte pas la 4G"},
            {"role": "assistant", "content": "Je vais vous aider à résoudre ce problème de 4G. Vérifiez d'abord que la 4G est activée dans les paramètres de votre téléphone."},
            {"role": "user", "content": "C'est déjà activé mais ça ne marche toujours pas"},
            {"role": "assistant", "content": "Essayez de redémarrer votre téléphone et vérifiez que vous êtes dans une zone couverte par Free Mobile. Si le problème persiste, contactez notre service technique."}
        ],
        "intent": "technique",
        "category": "technique",
        "sentiment": "neutral"
    })
    
    # Conversation résiliation
    conversations.append({
        "messages": [
            {"role": "user", "content": "Je veux résilier mon forfait"},
            {"role": "assistant", "content": "Je comprends que vous souhaitez résilier votre forfait. Pouvez-vous me dire pourquoi vous voulez partir ? Peut-être pouvons-nous trouver une solution."},
            {"role": "user", "content": "Je ne suis pas satisfait du service"},
            {"role": "assistant", "content": "Je suis désolé que vous ne soyez pas satisfait. Vous pouvez résilier depuis votre espace client ou nous contacter au 3244. La résiliation prend effet à la fin de votre période de facturation."}
        ],
        "intent": "resiliation",
        "category": "resiliation",
        "sentiment": "negative"
    })
    
    return conversations


def split_dataset(dataset: List[Dict[str, Any]], train_ratio: float = 0.8) -> tuple:
    """Divise le dataset en train et validation"""
    random.shuffle(dataset)
    split_idx = int(len(dataset) * train_ratio)
    
    train_data = dataset[:split_idx]
    val_data = dataset[split_idx:]
    
    return train_data, val_data


def save_jsonl(data: List[Dict[str, Any]], filepath: Path):
    """Sauvegarde les données au format JSONL"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def main():
    """Fonction principale"""
    # Chemins
    data_path = Path("data")
    processed_path = data_path / "processed"
    processed_path.mkdir(exist_ok=True)
    
    print("🔄 Préparation des datasets...")
    
    # Chargement des FAQs
    print("📚 Chargement des FAQs...")
    faqs = load_faqs(data_path)
    print(f"✅ {len(faqs)} FAQs chargées")
    
    # Création des variations
    print("🔄 Création des variations...")
    variations = create_training_variations(faqs)
    print(f"✅ {len(variations)} variations créées")
    
    # Création des conversations
    print("💬 Création des conversations...")
    conversations = create_conversation_examples()
    print(f"✅ {len(conversations)} conversations créées")
    
    # Combinaison des données
    all_data = variations + conversations
    
    # Division train/validation
    print("📊 Division train/validation...")
    train_data, val_data = split_dataset(all_data)
    print(f"✅ Train: {len(train_data)} échantillons")
    print(f"✅ Validation: {len(val_data)} échantillons")
    
    # Sauvegarde
    print("💾 Sauvegarde...")
    save_jsonl(train_data, processed_path / "training_set.jsonl")
    save_jsonl(val_data, processed_path / "validation_set.jsonl")
    
    # Statistiques
    print("\n📊 Statistiques:")
    print(f"Total échantillons: {len(all_data)}")
    print(f"Train: {len(train_data)} ({len(train_data)/len(all_data)*100:.1f}%)")
    print(f"Validation: {len(val_data)} ({len(val_data)/len(all_data)*100:.1f}%)")
    
    # Répartition par catégorie
    categories = {}
    for item in all_data:
        cat = item.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📈 Répartition par catégorie:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} ({count/len(all_data)*100:.1f}%)")
    
    print("\n✅ Préparation terminée !")


if __name__ == "__main__":
    main()


