# 🚀 Scripts de Lancement - CallCenter

Tous les scripts sont maintenant dans ce dossier `Transformer/`.

## 📂 Organisation

```
Transformer/
├── start_all.sh          ← Lance MLflow + API (RECOMMANDÉ)
├── start_project.sh      ← Lance l'API seule
├── start_mlflow.sh       ← Lance MLflow seul
├── test_api.sh           ← Tests complets de l'API
├── test_api_quick.sh     ← Tests rapides
└── stop_all.sh           ← Arrête tout
```

---

## 🎯 Utilisation

### **Lancement Complet (Recommandé)** ⭐

```bash
cd /home/louay/Desktop/Project/CallCenter/Transformer
./start_all.sh
```

**Lance :**
- 📊 MLflow UI → http://localhost:5000
- 🤖 API FastAPI → http://localhost:8000
- 📈 Monitoring automatique

---

### **Lancement Séparé**

**Option 1 : API seule**
```bash
./start_project.sh
```

**Option 2 : MLflow seul**
```bash
./start_mlflow.sh
```

---

### **Tests**

**Tests complets :**
```bash
./test_api.sh
```

**Tests rapides :**
```bash
./test_api_quick.sh
```

---

### **Arrêt**

```bash
./stop_all.sh
```

Ou simplement `CTRL + C` dans le terminal.

---

## 🔗 Liens Utiles

- 📚 **Documentation API** : http://localhost:8000/docs
- 📊 **MLflow UI** : http://localhost:5000
- 🤗 **Modèle HF** : https://huggingface.co/Kahouli/callcenter-ticket-classifier

---

## 💡 Notes

- Les scripts utilisent des **chemins absolus**, vous pouvez les lancer de n'importe où
- Le modèle est chargé depuis **Hugging Face** (téléchargement automatique au 1er lancement)
- MLflow est **optionnel** - l'API fonctionne sans lui
- Tout est dans le **virtual environment** `.venv/`
