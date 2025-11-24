# Frontend IA Agent

Interface React moderne pour l'agent IA du centre d'appels.

## 🚀 Fonctionnalités

- 💬 Interface de chat conversationnelle
- 📱 Design responsive avec Tailwind CSS
- 💾 Sauvegarde des conversations dans localStorage
- 🎨 Interface moderne avec mode sombre
- ⚡ Rapide et réactive avec Vite

## 📦 Installation

```bash
cd ia_agent/frontend
npm install
```

## 🛠️ Développement

Lancer le serveur de développement :

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

## 🏗️ Build

Créer une version de production :

```bash
npm run build
```

Les fichiers seront générés dans le dossier `dist/`

## 📝 Configuration

### API Backend

L'interface est configurée pour se connecter à l'API Anthropic Claude. 

Pour modifier l'endpoint de l'API, éditez le fichier `src/components/ChatInterface.jsx` :

```javascript
const response = await fetch('https://api.anthropic.com/v1/messages', {
  // ... configuration
});
```

### Proxy Vite

Un proxy est configuré dans `vite.config.js` pour rediriger les requêtes `/api` vers `http://localhost:8000`

## 🎨 Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ChatInterface.jsx  # Composant principal du chat
│   ├── App.jsx                # Composant racine
│   ├── main.jsx              # Point d'entrée
│   ├── App.css               # Styles globaux
│   └── index.css             # Styles Tailwind
├── index.html                # Template HTML
├── package.json              # Dépendances
├── vite.config.js           # Configuration Vite
├── tailwind.config.js       # Configuration Tailwind
└── postcss.config.js        # Configuration PostCSS
```

## 📚 Technologies utilisées

- **React 18** - Framework UI
- **Vite** - Build tool rapide
- **Tailwind CSS** - Framework CSS utility-first
- **Lucide React** - Icônes modernes
- **LocalStorage** - Persistance des données

## 🔧 Scripts disponibles

- `npm run dev` - Lance le serveur de développement
- `npm run build` - Crée une version de production
- `npm run preview` - Prévisualise la version de production
- `npm run lint` - Vérifie le code avec ESLint

## 🌟 Fonctionnalités du Chat

1. **Conversations multiples** - Gérez plusieurs conversations simultanément
2. **Historique persistant** - Les conversations sont sauvegardées localement
3. **Interface intuitive** - Design inspiré de ChatGPT
4. **Raccourcis clavier** - Entrée pour envoyer, Shift+Entrée pour nouvelle ligne
5. **Indicateur de chargement** - Animation pendant le traitement
6. **Gestion d'erreurs** - Messages d'erreur conviviaux

## 📄 Licence

MIT
