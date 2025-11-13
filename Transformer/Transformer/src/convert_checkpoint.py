import os
import shutil
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def convert_colab_checkpoint(colab_model_path, local_model_path):
    """
    Convertit et copie le modèle depuis Google Colab vers le projet local.
    
    Args:
        colab_model_path (str): Chemin vers le modèle sur Google Drive
        local_model_path (str): Chemin de destination dans le projet local
    """
    print(f"Converting model from {colab_model_path} to {local_model_path}")
    
    # Créer le dossier de destination s'il n'existe pas
    os.makedirs(local_model_path, exist_ok=True)
    
    try:
        # Charger le modèle et le tokenizer depuis Google Drive
        model = AutoModelForSequenceClassification.from_pretrained(colab_model_path)
        tokenizer = AutoTokenizer.from_pretrained(colab_model_path)
        
        # Charger les mappings des labels
        with open(os.path.join(colab_model_path, 'label_mappings.json'), 'r') as f:
            label_mappings = json.load(f)
        
        # Sauvegarder dans le projet local
        model.save_pretrained(local_model_path)
        tokenizer.save_pretrained(local_model_path)
        
        # Copier les mappings des labels
        with open(os.path.join(local_model_path, 'label_mappings.json'), 'w') as f:
            json.dump(label_mappings, f, indent=2)
            
        print("Conversion terminée avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la conversion : {str(e)}")
        raise

if __name__ == "__main__":
    # Chemins par défaut
    colab_model_path = "/content/drive/MyDrive/CallCenter/models/best_model"
    local_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "models", "transformer", "best_model")
    
    # Convertir le modèle
    convert_colab_checkpoint(colab_model_path, local_model_path)
