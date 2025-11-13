"""
Script pour tester l'API Hugging Face après déploiement
Usage: python test_hf_api.py
"""

import requests
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Configuration
HF_USERNAME = "louaykahouli"  # Votre username
MODEL_NAME = "callcenter-ticket-classifier"
REPO_ID = f"{HF_USERNAME}/{MODEL_NAME}"

# Exemples de tickets à tester
TEST_TICKETS = [
    "Mon ordinateur portable ne s'allume plus, l'écran reste noir",
    "Je n'arrive pas à me connecter au VPN de l'entreprise",
    "J'ai besoin d'acheter de nouvelles licences Office pour mon équipe",
    "Le serveur de fichiers est très lent aujourd'hui",
    "Je voudrais prendre mes congés la semaine prochaine",
]

def test_with_api(hf_token=None):
    """Teste le modèle via l'API Inference de Hugging Face"""
    print("🔥 Test via API Inference de Hugging Face")
    print("=" * 60)
    
    if not hf_token:
        print("⚠️  Pas de token fourni, tentative sans authentification...")
        print("Note : Vous pouvez obtenir un token sur https://huggingface.co/settings/tokens\n")
    
    API_URL = f"https://api-inference.huggingface.co/models/{REPO_ID}"
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    
    for i, ticket in enumerate(TEST_TICKETS, 1):
        print(f"\n📋 Ticket {i} : {ticket}")
        
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": ticket}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Résultat : {json.dumps(result[0] if isinstance(result, list) else result, indent=2)}")
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur : {e}")

def test_with_transformers():
    """Teste le modèle en le chargeant directement avec transformers"""
    print("\n\n🤗 Test via chargement direct du modèle")
    print("=" * 60)
    print(f"Chargement du modèle {REPO_ID}...\n")
    
    try:
        # Charger le modèle et le tokenizer
        tokenizer = AutoTokenizer.from_pretrained(REPO_ID)
        model = AutoModelForSequenceClassification.from_pretrained(REPO_ID)
        model.eval()
        
        print("✅ Modèle chargé avec succès!\n")
        
        # Tester chaque ticket
        for i, ticket in enumerate(TEST_TICKETS, 1):
            print(f"📋 Ticket {i} : {ticket}")
            
            # Tokenizer
            inputs = tokenizer(
                ticket,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            )
            
            # Prédiction
            with torch.no_grad():
                outputs = model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_class = torch.argmax(predictions, dim=-1).item()
                confidence = predictions[0][predicted_class].item()
            
            print(f"✅ Catégorie prédite : {predicted_class}")
            print(f"   Confiance : {confidence:.2%}\n")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("\n💡 Si le modèle n'est pas trouvé, assurez-vous de l'avoir déployé avec :")
        print("   python deploy_to_huggingface.py")

if __name__ == "__main__":
    print("🎯 Test du modèle CallCenter sur Hugging Face")
    print("=" * 60)
    print(f"Modèle : {REPO_ID}\n")
    
    # Option 1 : Test avec l'API
    hf_token = input("Entrez votre token Hugging Face (ou appuyez sur Entrée pour passer) : ").strip()
    if hf_token:
        test_with_api(hf_token)
    else:
        print("⏭️  Test API ignoré (pas de token)\n")
    
    # Option 2 : Test en chargeant le modèle
    print("\n" + "=" * 60)
    response = input("Voulez-vous tester en chargeant le modèle localement ? (o/n) : ").strip().lower()
    if response == 'o':
        test_with_transformers()
    
    print("\n✅ Tests terminés!")
