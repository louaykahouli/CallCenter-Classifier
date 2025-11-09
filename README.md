# 🎯 CallCenter Ticket Classifier

Système intelligent de classification automatique de tickets avec **Transformer (DistilBERT)**, déployé sur **Hugging Face**, avec monitoring **MLflow** et API **FastAPI**.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Transformers](https://img.shields.io/badge/Transformers-4.0+-orange.svg)](https://huggingface.co/transformers/)
[![MLflow](https://img.shields.io/badge/MLflow-2.0+-blue.svg)](https://mlflow.org/)

---

## 🌟 Fonctionnalités

- ✅ **Classification automatique** de tickets en 8 catégories
- 🤗 **Modèle sur HuggingFace** : `Kahouli/callcenter-ticket-classifier`
- 🚀 **API REST** avec FastAPI (endpoints synchrones et batch)
- 📊 **Monitoring MLflow** pour tracking des prédictions
- 🔄 **Pipeline MLOps** complet et automatisé
- 📈 **Métriques en temps réel** (temps d'inférence, confiance, distribution)

---

## 📦 Catégories

Le modèle classe les tickets dans ces 8 catégories :

| Catégorie | Description |
|-----------|-------------|
| **Hardware** | Problèmes matériels (ordinateur, imprimante, etc.) |
| **Access** | Problèmes d'accès (VPN, serveur, droits) |
| **Miscellaneous** | Divers |
| **HR Support** | Ressources humaines (congés, formation) |
| **Purchase** | Achats et commandes |
| **Administrative rights** | Droits administrateurs |
| **Storage** | Stockage et espace disque |
| **Internal Project** | Projets internes |

---

## 🚀 Démarrage Rapide

### **1. Cloner le projet**

```bash
git clone https://github.com/louaykahouli/CallCenter-Classifier.git
cd CallCenter-Classifier
```

### **2. Créer l'environnement virtuel**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### **3. Installer les dépendances**

```bash
pip install -r Transformer/requirements.txt
```

### **4. Lancer le projet**

```bash
cd Transformer
./start_all.sh
```

**Accès :**
- 🤖 **API** : http://localhost:8000
- 📚 **Documentation** : http://localhost:8000/docs
- 📊 **MLflow UI** : http://localhost:5000

---

## 🔧 Utilisation de l'API

### **Classification simple**

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Mon ordinateur ne démarre plus"}'
```

**Réponse :**
```json
{
  "predicted_category": "Hardware",
  "confidence": 0.95,
  "all_predictions": {
    "Hardware": 0.95,
    "Access": 0.03,
    "Miscellaneous": 0.02
  }
}
```

### **Classification batch**

```bash
curl -X POST http://localhost:8000/classify-batch \
  -H "Content-Type: application/json" \
  -d '{
    "tickets": [
      "Mon ordinateur ne démarre plus",
      "Je ne peux pas accéder au serveur"
    ]
  }'
```

---

## 📂 Structure du Projet

```
CallCenter/
├── Transformer/
│   ├── api/                    # API FastAPI
│   │   ├── main.py            # Point d'entrée
│   │   └── config.py          # Configuration
│   │
│   ├── src/                   # Code source
│   │   ├── train_transformer.py
│   │   ├── predict.py
│   │   └── data_preprocessing.py
│   │
│   ├── tests/                 # Tests unitaires
│   │   └── test_api.py
│   │
│   ├── notebooks/             # Notebooks Jupyter
│   │
│   ├── start_all.sh          # Lance MLflow + API
│   ├── start_project.sh      # Lance API seule
│   ├── test_api.sh           # Tests manuels
│   └── requirements.txt      # Dépendances
│
└── README.md
```

---

## 🤗 Modèle HuggingFace

**Modèle** : [`Kahouli/callcenter-ticket-classifier`](https://huggingface.co/Kahouli/callcenter-ticket-classifier)

- **Base** : `distilbert-base-multilingual-cased`
- **Taille** : 541 MB
- **Langues** : Multilingue (français, anglais, etc.)
- **Téléchargement automatique** au premier lancement

---

## 📊 Monitoring avec MLflow

MLflow suit automatiquement :
- ⏱️ **Temps d'inférence** par prédiction
- 📈 **Confiance** des prédictions
- 📊 **Distribution des catégories**
- 🔢 **Nombre de prédictions**

Accédez au tableau de bord : http://localhost:5000

---

## 🧪 Tests

### **Tests manuels (curl)**
```bash
./test_api.sh
```

### **Tests unitaires (pytest)**
```bash
pytest tests/test_api.py -v
```

---

## 📚 Documentation

- **Guide de démarrage** : `Transformer/README.md`
- **Guide MLflow** : `Transformer/MLFLOW_GUIDE.md`
- **Guide des tests** : `Transformer/GUIDE_TESTS.md`
- **Scripts** : `Transformer/SCRIPTS_README.md`

---

## 🛠️ Technologies

- **Python** 3.8+
- **FastAPI** - Framework API moderne
- **Transformers** - Bibliothèque Hugging Face
- **PyTorch** - Backend ML
- **MLflow** - Tracking et monitoring
- **Uvicorn** - Serveur ASGI

---

## 📈 Performance

- **Accuracy** : ~95%
- **F1-Score** : ~94%
- **Temps d'inférence** : ~100-200ms par ticket

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT.

---

## 👤 Auteur

**Louay Kahouli**

- GitHub: [@louaykahouli](https://github.com/louaykahouli)
- HuggingFace: [@Kahouli](https://huggingface.co/Kahouli)

---

## 🙏 Remerciements

- [Hugging Face](https://huggingface.co/) pour l'hébergement du modèle
- [FastAPI](https://fastapi.tiangolo.com/) pour le framework
- [MLflow](https://mlflow.org/) pour le tracking
