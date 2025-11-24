# 🧪 Exemples de Tests pour le Frontend - Agent IA

## 📝 Textes de TEST par Niveau de Complexité

### 🟢 COMPLEXITÉ BASSE (Score < 30) → Utilise TF-IDF
**Caractéristiques:** Textes courts, vocabulaire simple, direct

```
Imprimante cassée
```

```
Souris ne marche pas
```

```
Mot de passe oublié
```

```
Écran noir
```

```
Besoin badge
```

---

### 🟡 COMPLEXITÉ MOYENNE (Score 30-49) → Utilise TF-IDF
**Caractéristiques:** Textes de longueur moyenne, quelques détails

```
Je n'arrive pas à me connecter au VPN de l'entreprise depuis ce matin
```

```
Mon ordinateur redémarre tout seul plusieurs fois par jour
```

```
Impossible d'accéder au dossier partagé du département RH
```

```
Ma boîte mail ne synchronise plus les nouveaux messages depuis hier
```

```
Le logiciel de gestion refuse de s'ouvrir après la dernière mise à jour
```

---

### 🔴 HAUTE COMPLEXITÉ (Score ≥ 50) → Utilise Transformer
**Caractéristiques:** Textes longs, vocabulaire technique, contexte détaillé

```
Plusieurs utilisateurs du département RH signalent des problèmes d'accès intermittents au serveur partagé depuis l'installation du nouveau pare-feu la semaine dernière, notamment lors de la connexion via VPN
```

```
Suite à la migration vers le nouveau système de gestion des tickets, je rencontre des difficultés pour accéder à l'interface d'administration et les permissions semblent incorrectement configurées malgré mon statut de super administrateur
```

```
Les employés du site distant de Lyon rapportent des lenteurs importantes lors du téléchargement de fichiers volumineux depuis le serveur central, particulièrement pendant les heures de pointe entre 9h et 11h, ce qui impacte significativement leur productivité
```

```
Après l'installation de la dernière mise à jour de sécurité Windows sur l'ensemble du parc informatique, plusieurs postes de travail du département comptabilité rencontrent des problèmes de compatibilité avec le logiciel de facturation SAP, entraînant des erreurs critiques lors de la génération des rapports mensuels
```

```
Je constate que depuis le déploiement du nouveau système d'authentification multi-facteurs combiné avec la migration vers Office 365, un nombre croissant d'utilisateurs éprouvent des difficultés pour accéder à leurs emails via Outlook, particulièrement ceux qui utilisent des connexions VPN établies depuis des réseaux externes non sécurisés
```

---

## 🎯 Comment Tester dans le Frontend

1. **Ouvrez le frontend:** http://localhost:3000
2. **Copiez-collez** un des textes ci-dessus dans la zone de saisie
3. **Appuyez sur Entrée** ou cliquez sur le bouton d'envoi
4. **Observez la réponse** qui contient:
   - 🎯 La catégorie prédite
   - 🤖 Le modèle utilisé (TFIDF ou TRANSFORMER)
   - 📊 Le score de complexité
   - 📈 Les probabilités pour chaque catégorie
   - 💡 L'explication du routage

---

## 🔥 Test Recommandé pour HAUTE COMPLEXITÉ

### **Exemple optimal pour déclencher le Transformer:**

```
Dans le cadre du déploiement de la nouvelle infrastructure cloud Azure, plusieurs utilisateurs du département informatique signalent des problèmes persistants de synchronisation avec Active Directory, notamment concernant la réplication des groupes de sécurité et des stratégies de groupe GPO, ce qui entraîne des incohérences au niveau des permissions d'accès aux ressources partagées et aux applications métier critiques hébergées sur les serveurs de production
```

**Pourquoi ce texte déclenche le Transformer:**
- ✅ Longueur: 89 mots (score élevé)
- ✅ Vocabulaire technique dense (Azure, Active Directory, GPO, réplication, etc.)
- ✅ Structure complexe avec plusieurs propositions subordonnées
- ✅ Contexte détaillé et multi-facettes
- ✅ **Score attendu: > 60/100**

---

## 📊 Comparaison des Modèles

### Test A/B - Même problème, complexité différente:

**Version Simple (→ TF-IDF):**
```
Problème Active Directory
```

**Version Complexe (→ Transformer):**
```
Depuis la migration de notre infrastructure Active Directory vers Azure AD, nous rencontrons des problèmes de synchronisation des identités utilisateurs entre les environnements on-premise et cloud, ce qui impacte l'authentification SSO pour plusieurs applications SaaS critiques
```

---

## 🎭 Catégories Possibles

Les modèles peuvent prédire ces catégories:
- **Hardware** - Problèmes matériels
- **Access** - Droits et accès
- **HR Support** - Support RH
- **Administrative rights** - Droits administratifs
- **Storage** - Stockage
- **Purchase** - Achats
- **Internal Project** - Projets internes
- **Miscellaneous** - Divers

Testez différents types de problèmes pour voir comment l'agent les classifie!
