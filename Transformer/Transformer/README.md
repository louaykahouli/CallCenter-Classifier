# 🎯 CallCenter - Classification Intelligente de Tickets

Système de classification automatique de tickets avec Transformer (DistilBERT) déployé sur Hugging Face, API FastAPI et monitoring MLflow.

---

## 🚀 Démarrage Rapide

### **Lancement Complet (Recommandé)**

```bash
cd /home/louay/Desktop/Project/CallCenter/Transformer
./start_all.sh
```

**Lance :**
- 📊 MLflow UI → http://localhost:5000
- 🤖 API FastAPI → http://localhost:8000
- 📈 Monitoring automatique

### **Tests**

```bash
./test_api.sh
```

---

## 📂 Structure du Projet

```
Transformer/
├── api/                      # API FastAPI
│   ├── main.py              # Point d'entrée
│   ├── config.py            # Configuration
│   └── .env                 # Variables d'environnement
│
├── src/                     # Code source
│   ├── train_transformer.py # Entraînement
│   └── predict.py           # Prédiction
│
├── tests/                   # Tests unitaires
│   └── test_api.py         
│
├── start_all.sh            # Lance MLflow + API
├── start_project.sh        # Lance API seule
├── start_mlflow.sh         # Lance MLflow seul
├── test_api.sh             # Tests complets
└── stop_all.sh             # Arrête tout
```

---

## 🔧 Scripts Disponibles

| Script | Description |
|--------|-------------|
| `./start_all.sh` | Lance MLflow + API (recommandé) |
| `./start_project.sh` | Lance l'API seule |
| `./start_mlflow.sh` | Lance MLflow seul |
| `./test_api.sh` | Tests complets de l'API |
| `./test_api_quick.sh` | Tests rapides |
| `./stop_all.sh` | Arrête tous les processus |

---

## 🤗 Modèle Hugging Face

**Modèle :** `Kahouli/callcenter-ticket-classifier`  
**Lien :** https://huggingface.co/Kahouli/callcenter-ticket-classifier

Le modèle est téléchargé automatiquement au premier lancement (541 MB).

---

## 📊 Catégories

- Hardware
- Access
- Miscellaneous
- HR Support
- Purchase
- Administrative rights
- Storage
- Internal Project

---

## 📚 Documentation

- **Guide Principal** : `GUIDE_DEMARRAGE.md`
- **Guide MLflow** : `MLFLOW_GUIDE.md`
- **Guide Tests** : `GUIDE_TESTS.md`
- **Scripts** : `SCRIPTS_README.md`

---

## 🔗 Liens Utiles

- 📚 API Docs : http://localhost:8000/docs
- 📊 MLflow UI : http://localhost:5000
- 🤗 Modèle : https://huggingface.co/Kahouli/callcenter-ticket-classifier
