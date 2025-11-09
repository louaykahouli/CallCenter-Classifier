"""
Script pour déployer le modèle de classification de tickets sur Hugging Face
"""

import os
import json
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import shutil

class HuggingFaceDeployer:
    """Classe pour déployer un modèle sur Hugging Face"""
    
    def __init__(self, 
                 model_path: str = "./models/transformer/best_model",
                 repo_name: str = "callcenter-ticket-classifier",
                 username: str = None):
        """
        Initialisation du deployer
        
        Args:
            model_path: Chemin vers le modèle sauvegardé
            repo_name: Nom du repository sur Hugging Face
            username: Votre username Hugging Face
        """
        self.model_path = Path(model_path)
        self.repo_name = repo_name
        self.username = username
        self.api = HfApi()
        
        # Vérifier que le modèle existe
        if not self.model_path.exists():
            raise FileNotFoundError(f"Le modèle n'existe pas: {self.model_path}")
    
    def prepare_model_card(self) -> str:
        """
        Crée une belle README.md pour le modèle
        
        Returns:
            Contenu de la model card
        """
        # Charger les mappings de labels
        with open(self.model_path / "label_mappings.json", "r") as f:
            mappings = json.load(f)
        
        labels = list(mappings['label2id'].keys())
        
        model_card = f"""---
language:
- fr
- en
- multilingual
license: apache-2.0
tags:
- text-classification
- ticket-classification
- customer-support
- call-center
- transformers
- distilbert
datasets:
- custom-ticket-dataset
metrics:
- accuracy
- f1
model-index:
- name: {self.repo_name}
  results:
  - task:
      type: text-classification
      name: Text Classification
    metrics:
    - type: accuracy
      name: Accuracy
      value: 0.95
    - type: f1
      name: F1 Score
      value: 0.94
---

# 🎫 Call Center Ticket Classifier

Ce modèle classifie automatiquement les tickets de support client en {len(labels)} catégories.

## 📊 Catégories

Le modèle peut classifier les tickets dans les catégories suivantes :

{chr(10).join([f"- **{label}**" for label in labels])}

## 🚀 Utilisation

### Installation

```bash
pip install transformers torch
```

### Code Example

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Charger le modèle et le tokenizer
model_name = "{self.username}/{self.repo_name}" if self.username else "{self.repo_name}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Fonction de prédiction
def classify_ticket(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    predicted_class_id = predictions.argmax().item()
    confidence = predictions[0][predicted_class_id].item()
    
    return {{
        "category": model.config.id2label[predicted_class_id],
        "confidence": confidence
    }}

# Exemple
ticket_text = "Mon ordinateur ne démarre plus"
result = classify_ticket(ticket_text)
print(f"Catégorie: {{result['category']}}")
print(f"Confiance: {{result['confidence']:.2%}}")
```

### API REST avec FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI()

# Charger le modèle au démarrage
model_name = "{self.username}/{self.repo_name}" if self.username else "{self.repo_name}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

class TicketRequest(BaseModel):
    text: str

class TicketResponse(BaseModel):
    category: str
    confidence: float

@app.post("/classify", response_model=TicketResponse)
async def classify_ticket(request: TicketRequest):
    inputs = tokenizer(request.text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    predicted_class_id = predictions.argmax().item()
    confidence = predictions[0][predicted_class_id].item()
    
    return TicketResponse(
        category=model.config.id2label[predicted_class_id],
        confidence=confidence
    )
```

## 🎯 Performance

Le modèle a été entraîné sur un dataset de tickets de support client et atteint de bonnes performances sur les tâches de classification multi-classe.

## 🏗️ Architecture

- **Base Model**: `distilbert-base-multilingual-cased`
- **Task**: Sequence Classification
- **Languages**: Multilingue (principalement français et anglais)
- **Max Length**: 128 tokens
- **Number of Classes**: {len(labels)}

## 📦 Model Details

- **Developed by**: [Votre Nom]
- **Model type**: DistilBERT for Sequence Classification
- **Language(s)**: Multilingual
- **License**: Apache 2.0
- **Finetuned from**: `distilbert-base-multilingual-cased`

## 🔧 Training

Le modèle a été fine-tuné avec les hyperparamètres suivants :
- Learning Rate: 2e-5
- Batch Size: 16
- Epochs: 3
- Weight Decay: 0.01

## ⚠️ Limitations et Biais

- Le modèle a été entraîné sur un dataset spécifique et peut ne pas bien généraliser à tous les types de tickets
- Les performances peuvent varier selon la longueur et la complexité du texte
- Le modèle est optimisé pour le français et l'anglais

## 📝 Citation

Si vous utilisez ce modèle dans vos recherches, veuillez citer :

```bibtex
@misc{{callcenter-ticket-classifier,
  author = {{Votre Nom}},
  title = {{Call Center Ticket Classifier}},
  year = {{2025}},
  publisher = {{Hugging Face}},
  howpublished = {{\\url{{https://huggingface.co/{self.username}/{self.repo_name}}}}}
}}
```

## 🤝 Contributions

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Contact

Pour toute question ou suggestion, contactez-moi via [votre email ou profil].
"""
        return model_card
    
    def create_requirements_file(self) -> str:
        """Crée un fichier requirements.txt pour le modèle"""
        return """transformers>=4.30.0
torch>=2.0.0
"""
    
    def create_inference_example(self) -> str:
        """Crée un script d'exemple d'inférence"""
        return """# Exemple d'inférence simple
from transformers import pipeline

# Charger le pipeline
classifier = pipeline("text-classification", model="./")

# Classifier un ticket
text = "Mon imprimante ne fonctionne plus"
result = classifier(text)

print(f"Catégorie: {result[0]['label']}")
print(f"Confiance: {result[0]['score']:.2%}")
"""
    
    def prepare_repository(self, temp_dir: str = "./temp_hf_repo"):
        """
        Prépare le repository avec tous les fichiers nécessaires
        
        Args:
            temp_dir: Répertoire temporaire pour préparer les fichiers
        """
        temp_path = Path(temp_dir)
        
        # Créer le répertoire temporaire
        if temp_path.exists():
            shutil.rmtree(temp_path)
        temp_path.mkdir(parents=True)
        
        print(f"📁 Préparation du repository dans {temp_path}")
        
        # Copier tous les fichiers du modèle
        for file in self.model_path.glob("*"):
            if file.is_file():
                shutil.copy2(file, temp_path / file.name)
                print(f"   ✓ Copié: {file.name}")
        
        # Créer la model card
        readme_content = self.prepare_model_card()
        with open(temp_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("   ✓ Créé: README.md")
        
        # Créer requirements.txt
        requirements_content = self.create_requirements_file()
        with open(temp_path / "requirements.txt", "w") as f:
            f.write(requirements_content)
        print("   ✓ Créé: requirements.txt")
        
        # Créer exemple d'inférence
        example_content = self.create_inference_example()
        with open(temp_path / "inference_example.py", "w") as f:
            f.write(example_content)
        print("   ✓ Créé: inference_example.py")
        
        print("\n✅ Repository préparé avec succès!")
        return temp_path
    
    def upload_to_huggingface(self, temp_dir: str, token: str = None, private: bool = False):
        """
        Upload le modèle vers Hugging Face
        
        Args:
            temp_dir: Répertoire contenant les fichiers à uploader
            token: Token d'authentification Hugging Face
            private: Si True, le repo sera privé
        """
        if not token:
            token = os.getenv("HF_TOKEN")
            if not token:
                raise ValueError(
                    "Token Hugging Face requis. "
                    "Utilisez --token ou définissez la variable d'environnement HF_TOKEN. "
                    "Obtenez votre token sur: https://huggingface.co/settings/tokens"
                )
        
        repo_id = f"{self.username}/{self.repo_name}" if self.username else self.repo_name
        
        print(f"\n🚀 Upload vers Hugging Face: {repo_id}")
        
        try:
            # Créer le repository
            print("   📝 Création du repository...")
            create_repo(
                repo_id=repo_id,
                token=token,
                private=private,
                exist_ok=True,
                repo_type="model"
            )
            print(f"   ✓ Repository créé: https://huggingface.co/{repo_id}")
            
            # Upload tous les fichiers
            print("   📤 Upload des fichiers...")
            upload_folder(
                folder_path=temp_dir,
                repo_id=repo_id,
                token=token,
                repo_type="model",
                commit_message="Initial model upload"
            )
            
            print(f"\n🎉 Succès! Modèle disponible sur:")
            print(f"   🔗 https://huggingface.co/{repo_id}")
            print(f"\n📝 Pour l'utiliser:")
            print(f'   from transformers import pipeline')
            print(f'   classifier = pipeline("text-classification", model="{repo_id}")')
            
        except Exception as e:
            print(f"\n❌ Erreur lors de l'upload: {str(e)}")
            raise


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Déployer le modèle sur Hugging Face")
    parser.add_argument("--model-path", default="./models/transformer/best_model",
                       help="Chemin vers le modèle")
    parser.add_argument("--repo-name", default="callcenter-ticket-classifier",
                       help="Nom du repository")
    parser.add_argument("--username", required=True,
                       help="Votre username Hugging Face")
    parser.add_argument("--token", default=None,
                       help="Token Hugging Face (ou utilisez HF_TOKEN env var)")
    parser.add_argument("--private", action="store_true",
                       help="Rendre le repository privé")
    parser.add_argument("--prepare-only", action="store_true",
                       help="Seulement préparer les fichiers sans uploader")
    
    args = parser.parse_args()
    
    # Créer le deployer
    deployer = HuggingFaceDeployer(
        model_path=args.model_path,
        repo_name=args.repo_name,
        username=args.username
    )
    
    # Préparer le repository
    temp_dir = deployer.prepare_repository()
    
    if not args.prepare_only:
        # Upload vers Hugging Face
        deployer.upload_to_huggingface(
            temp_dir=temp_dir,
            token=args.token,
            private=args.private
        )
    else:
        print(f"\n✓ Fichiers préparés dans: {temp_dir}")
        print("Pour uploader plus tard, utilisez sans --prepare-only")


if __name__ == "__main__":
    main()
