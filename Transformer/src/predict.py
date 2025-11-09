import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import json
import os

class TicketClassifier:
    def __init__(self, model_path):
        """
        Initialise le classificateur de tickets.
        
        Args:
            model_path (str): Chemin vers le dossier contenant le modèle
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Charger le modèle et le tokenizer
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Charger les mappings des labels
        with open(os.path.join(model_path, 'label_mappings.json'), 'r') as f:
            mappings = json.load(f)
            self.id2label = mappings['id2label']
    
    def predict(self, text):
        """
        Prédit la catégorie d'un ticket.
        
        Args:
            text (str): Le texte du ticket à classifier
            
        Returns:
            tuple: (catégorie prédite, score de confiance)
        """
        # Tokenization
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        ).to(self.device)
        
        # Prédiction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            
            # Obtenir la meilleure prédiction
            pred_id = probabilities.argmax().item()
            confidence = probabilities.max().item()
            
            # Convertir l'ID en label
            predicted_label = self.id2label[str(pred_id)]
            
        return predicted_label, confidence

# Exemple d'utilisation
if __name__ == "__main__":
    model_path = "models/transformer/best_model"  # Chemin vers votre modèle converti
    
    # Créer le classificateur
    classifier = TicketClassifier(model_path)
    
    # Exemple de prédiction
    test_text = "Mon ordinateur ne démarre plus après la mise à jour"
    category, confidence = classifier.predict(test_text)
    
    print(f"Texte : {test_text}")
    print(f"Catégorie prédite : {category}")
    print(f"Score de confiance : {confidence:.2%}")