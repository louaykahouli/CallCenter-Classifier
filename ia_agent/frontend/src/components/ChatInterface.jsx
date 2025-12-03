import React, { useState, useEffect, useRef } from 'react';
import { Send, Plus, Menu, MessageSquare, Trash2, BarChart3, Zap } from 'lucide-react';

export default function ChatInterface() {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);
  const [titlesSynced, setTitlesSynced] = useState(false); // Pour ne synchro qu'une fois
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Mettre à jour automatiquement les titres depuis la DB APRÈS le chargement
  useEffect(() => {
    if (conversations.length > 0 && !titlesSynced) {
      syncConversationTitles();
      setTitlesSynced(true);
    }
  }, [conversations]); // Se déclenche quand conversations change

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const syncConversationTitles = async () => {
    console.log('🔄 Synchronisation des titres depuis la base de données...');
    
    // Travailler avec une copie des conversations actuelles
    const conversationsToCheck = conversations.filter(c => c.title === 'Nouvelle conversation');
    
    if (conversationsToCheck.length === 0) {
      console.log('ℹ️ Aucun titre à mettre à jour');
      return;
    }

    const updates = new Map(); // Map de convId -> nouveau titre

    for (const conv of conversationsToCheck) {
      try {
        const response = await fetch(`http://localhost:8002/history/${conv.sessionId}`);
        if (response.ok) {
          const historyData = await response.json();
          const convs = Array.isArray(historyData) ? historyData : (historyData.conversations || []);
          
          if (convs.length > 0 && convs[0].conversation_title && convs[0].prediction) {
            const categoryIcon = {
              'Hardware': '🖥️',
              'Access': '🔐',
              'Purchase': '🛒',
              'HR Support': '👥',
              'Internal Project': '📁',
              'Administrative rights': '⚙️',
              'Storage': '💾',
              'Miscellaneous': '📝'
            }[convs[0].prediction] || '📋';
            
            const newTitle = `${categoryIcon} ${convs[0].conversation_title}`;
            updates.set(conv.id, newTitle);
            console.log(`✅ Titre trouvé pour ${conv.sessionId}: ${newTitle}`);
          }
        }
      } catch (error) {
        console.error(`❌ Erreur lors de la synchro du titre pour ${conv.sessionId}:`, error);
      }
    }

    if (updates.size > 0) {
      console.log(`💾 Mise à jour de ${updates.size} titre(s)...`);
      setConversations(prevConversations => {
        const updated = prevConversations.map(c => {
          if (updates.has(c.id)) {
            return { ...c, title: updates.get(c.id) };
          }
          return c;
        });
        saveConversations(updated);
        return updated;
      });
    } else {
      console.log('ℹ️ Aucun titre à mettre à jour');
    }
  };

  const loadConversations = () => {
    const saved = localStorage.getItem('chatConversations');
    if (saved) {
      const convs = JSON.parse(saved);
      setConversations(convs);
      if (convs.length > 0) {
        loadConversation(convs[0].id);
      }
    } else {
      createNewConversation();
    }
  };

  const saveConversations = (convs) => {
    localStorage.setItem('chatConversations', JSON.stringify(convs));
  };

  const createNewConversation = () => {
    const newConv = {
      id: Date.now().toString(),
      sessionId: `session-${Date.now()}`, // Nouveau: session_id pour l'API
      title: 'Nouvelle conversation',
      messages: [],
      createdAt: new Date().toISOString()
    };
    const updated = [newConv, ...conversations];
    setConversations(updated);
    setCurrentConvId(newConv.id);
    setMessages([]);
    saveConversations(updated);
  };

  const loadConversation = (id) => {
    const conv = conversations.find(c => c.id === id);
    if (conv) {
      setCurrentConvId(id);
      setMessages(conv.messages || []);
    }
  };

  const deleteConversation = (id) => {
    const updated = conversations.filter(c => c.id !== id);
    setConversations(updated);
    saveConversations(updated);
    
    // Si on supprime la conversation courante
    if (currentConvId === id) {
      if (updated.length > 0) {
        // S'il reste des conversations, charger la première
        loadConversation(updated[0].id);
      } else {
        // S'il n'y a plus de conversations, réinitialiser l'état
        // SANS créer automatiquement une nouvelle conversation
        setCurrentConvId(null);
        setMessages([]);
      }
    }
  };

  // const updateConversationTitle = (id, newTitle) => {
  //   const updated = conversations.map(c => {
  //     if (c.id === id && c.title === 'Nouvelle conversation') {
  //       return { ...c, title: newTitle.substring(0, 50) };
  //     }
  //     return c;
  //   });
  //   setConversations(updated);
  //   saveConversations(updated);
  // };

  // const updateConversationMessages = (convId, newMessages) => {
  //   const updated = conversations.map(c => {
  //     if (c.id === convId) {
  //       return { ...c, messages: newMessages };
  //     }
  //     return c;
  //   });
  //   setConversations(updated);
  //   saveConversations(updated);
  // };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    // Sauvegarder l'input avant de le vider
    const messageText = input;
    setInput('');
    setIsLoading(true);

    // Si AUCUNE conversation n'existe, créer une nouvelle conversation automatiquement
    let convId = currentConvId;
    let sessionId = '';
    
    if (!currentConvId) {
      // Créer une nouvelle conversation uniquement s'il n'y en a pas
      const newConv = {
        id: Date.now().toString(),
        sessionId: `session-${Date.now()}`,
        title: 'Nouvelle conversation',
        messages: [],
        createdAt: new Date().toISOString()
      };
      const updated = [newConv, ...conversations];
      setConversations(updated);
      setCurrentConvId(newConv.id);
      convId = newConv.id;
      sessionId = newConv.sessionId;
      setMessages([]);
      saveConversations(updated);
      
      // Ajouter le message utilisateur
      const userMessage = {
        role: 'user',
        content: messageText,
        timestamp: new Date().toISOString()
      };
      setMessages([userMessage]);
      
      // Traiter la réponse
      await processMessage(messageText, convId, sessionId, [userMessage], updated);
    } else {
      // Utiliser la conversation existante (continuer la conversation comme ChatGPT)
      const currentConv = conversations.find(c => c.id === convId);
      sessionId = currentConv?.sessionId || `session-${Date.now()}`;
      
      const userMessage = {
        role: 'user',
        content: messageText,
        timestamp: new Date().toISOString()
      };
      
      const updatedMessages = [...messages, userMessage];
      setMessages(updatedMessages);
      
      // Traiter la réponse
      await processMessage(messageText, convId, sessionId, updatedMessages, conversations);
    }
  };

  const processMessage = async (messageText, convId, sessionId, updatedMessages, currentConversations) => {
    try {
      // Ne pas générer de titre ici - le backend (Grok) s'en occupera automatiquement
      
      // Appeler l'agent IA local avec session_id
      const response = await fetch('http://localhost:8002/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: messageText,
          session_id: sessionId
          // conversation_title sera généré automatiquement par Grok
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      
      // Générer un titre intelligent pour la première réponse
      if (updatedMessages.length === 1 && data.prediction) {
        console.log('🔍 DEBUG: Premier message détecté, récupération du titre...');
        console.log('🔍 Session ID:', sessionId);
        console.log('🔍 Conv ID:', convId);
        
        // Attendre un peu pour que la DB soit mise à jour
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Récupérer l'historique pour obtenir le titre généré par le backend
        try {
          const historyResponse = await fetch(`http://localhost:8002/history/${sessionId}`);
          console.log('🔍 Réponse /history status:', historyResponse.status);
          
          if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            console.log('🔍 Données historique:', historyData);
            
            // L'API retourne { session_id, count, conversations: [...] }
            const convs = Array.isArray(historyData) ? historyData : (historyData.conversations || []);
            console.log('🔍 Conversations trouvées:', convs.length);
            console.log('🔍 Premier titre:', convs[0]?.conversation_title);
            
            if (convs.length > 0 && convs[0].conversation_title) {
              // Ajouter l'icône selon la catégorie
              const categoryIcon = {
                'Hardware': '🖥️',
                'Access': '🔐',
                'Purchase': '🛒',
                'HR Support': '👥',
                'Internal Project': '📁',
                'Administrative rights': '⚙️',
                'Storage': '💾',
                'Miscellaneous': '📝'
              }[data.prediction] || '📋';
              
              const newTitle = `${categoryIcon} ${convs[0].conversation_title}`;
              
              console.log('📝 Mise à jour du titre:', newTitle);
              console.log('📝 Conversations actuelles:', currentConversations);
              
              // Mettre à jour le titre dans l'état local avec la forme fonctionnelle
              setConversations(prevConversations => {
                const updatedConversations = prevConversations.map(c => {
                  if (c.id === convId) {
                    console.log('✅ Conversation trouvée, mise à jour du titre');
                    return { ...c, title: newTitle };
                  }
                  return c;
                });
                console.log('📝 Conversations mises à jour:', updatedConversations);
                saveConversations(updatedConversations);
                return updatedConversations;
              });
            } else {
              console.warn('⚠️ Pas de titre dans l\'historique');
            }
          } else {
            console.warn('⚠️ Erreur HTTP lors de la récupération de l\'historique:', historyResponse.status);
          }
        } catch (titleError) {
          console.error('❌ Erreur lors de la récupération du titre:', titleError);
        }
      }
      
      // Ajouter un badge de cache si applicable
      const cacheIndicator = data.cache_hit ? '⚡ **Depuis le cache** ' : '';
      
      // Utiliser la réponse générée par Grok si disponible, sinon fallback
      const responseText = data.generated_response || `🎯 **Catégorie prédite:** ${data.prediction}

🤖 **Modèle utilisé:** ${data.model_used.toUpperCase()}

📊 **Analyse de complexité:**
- Score: ${data.complexity_analysis.score}/100
- Niveau: ${data.complexity_analysis.level}

📈 **Probabilités:**
${Object.entries(data.probabilities)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 3)
  .map(([cat, prob]) => `- ${cat}: ${(prob * 100).toFixed(2)}%`)
  .join('\n')}

💡 **Raisonnement:** ${data.reasoning}`;

      const assistantMessage = {
        role: 'assistant',
        content: `${cacheIndicator}${responseText}`,
        timestamp: new Date().toISOString(),
        metadata: {
          cache_hit: data.cache_hit,
          model_used: data.model_used,
          complexity_score: data.complexity_analysis.score,
          session_id: data.session_id
        }
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);
      
      // Mettre à jour les messages dans la conversation avec la forme fonctionnelle
      setConversations(prevConversations => {
        const updatedConversationsWithMessages = prevConversations.map(c => {
          if (c.id === convId) {
            return { ...c, messages: finalMessages };
          }
          return c;
        });
        saveConversations(updatedConversationsWithMessages);
        return updatedConversationsWithMessages;
      });
    } catch (error) {
      console.error('Erreur:', error);
      const errorMessage = {
        role: 'assistant',
        content: `❌ Désolé, une erreur s'est produite lors de la classification.\n\nErreur: ${error.message}\n\nAssurez-vous que l'agent IA est démarré (http://localhost:8002)`,
        timestamp: new Date().toISOString()
      };
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      
      // Mettre à jour les messages dans la conversation avec la forme fonctionnelle
      setConversations(prevConversations => {
        const updatedConversationsWithMessages = prevConversations.map(c => {
          if (c.id === convId) {
            return { ...c, messages: finalMessages };
          }
          return c;
        });
        saveConversations(updatedConversationsWithMessages);
        return updatedConversationsWithMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8002/stats');
      const data = await response.json();
      setStats(data);
      setShowStats(true);
    } catch (error) {
      console.error('Erreur lors de la récupération des stats:', error);
    }
  };

  const clearCache = async () => {
    try {
      await fetch('http://localhost:8002/cache/clear', { method: 'POST' });
      alert('Cache vidé avec succès !');
      fetchStats(); // Rafraîchir les stats
    } catch (error) {
      console.error('Erreur lors du vidage du cache:', error);
      alert('Erreur lors du vidage du cache');
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-gray-950 border-r border-gray-800 transition-all duration-300 overflow-hidden flex flex-col`}>
        <div className="p-4 border-b border-gray-800">
          <button
            onClick={createNewConversation}
            className="w-full flex items-center gap-2 px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <Plus size={20} />
            <span>Nouveau chat</span>
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2">
          {conversations.map(conv => (
            <div
              key={conv.id}
              className={`group relative mb-1 flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-colors ${
                currentConvId === conv.id ? 'bg-gray-800' : 'hover:bg-gray-800'
              }`}
              onClick={() => loadConversation(conv.id)}
            >
              <MessageSquare size={16} className="flex-shrink-0" />
              <span className="flex-1 truncate text-sm">{conv.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteConversation(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-700 rounded transition-opacity"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-14 border-b border-gray-800 flex items-center px-4 gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <Menu size={20} />
          </button>
          <h1 className="text-lg font-semibold">Agent IA - Classification de Tickets</h1>
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={fetchStats}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-sm"
            >
              <BarChart3 size={16} />
              <span>Statistiques</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-2xl px-4">
                <h2 className="text-4xl font-bold mb-4">🤖 Agent IA Intelligent</h2>
                <p className="text-gray-400 text-lg mb-6">Classificateur de tickets du centre d&apos;appels</p>
                <div className="text-left bg-gray-800 rounded-lg p-6 space-y-3">
                  <p className="text-gray-300 font-semibold">Comment ça marche ?</p>
                  <ul className="text-gray-400 space-y-2 text-sm">
                    <li>📝 Décrivez votre problème ou ticket</li>
                    <li>🧠 L&apos;agent analyse la complexité de votre texte</li>
                    <li>🎯 Il choisit automatiquement le meilleur modèle (TF-IDF ou Transformer)</li>
                    <li>📊 Vous recevez la catégorie prédite avec les probabilités</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto px-4 py-6">
              {messages.map((msg, idx) => (
                <div key={idx} className={`mb-6 ${msg.role === 'user' ? 'flex justify-end' : ''}`}>
                  <div className={`max-w-[85%] ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-2xl rounded-tr-sm' : 'bg-gray-800 rounded-2xl rounded-tl-sm'} px-5 py-3`}>
                    <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="mb-6">
                  <div className="max-w-[85%] bg-gray-800 rounded-2xl rounded-tl-sm px-5 py-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-800 p-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-3 items-end bg-gray-800 rounded-2xl p-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Écrivez votre message..."
                className="flex-1 bg-transparent resize-none outline-none px-3 py-2 max-h-32"
                rows="1"
                style={{ minHeight: '40px' }}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-xl transition-colors flex-shrink-0"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Modal */}
      {showStats && stats && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowStats(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">📊 Statistiques de l&apos;Agent IA</h2>
              <button
                onClick={() => setShowStats(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Cache Statistics */}
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Zap className="text-yellow-400" size={20} />
                  Cache Performance
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Entrées totales:</span>
                    <span className="font-semibold">{stats.cache_statistics?.total_entries || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Entrées actives:</span>
                    <span className="font-semibold text-green-400">{stats.cache_statistics?.active_entries || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Cache hits:</span>
                    <span className="font-semibold text-blue-400">{stats.cache_statistics?.total_hits || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">TTL:</span>
                    <span className="font-semibold">{stats.cache_statistics?.cache_ttl || 0}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Mémoire:</span>
                    <span className="font-semibold">{stats.cache_statistics?.memory_usage_mb || 0} MB</span>
                  </div>
                </div>
                <button
                  onClick={clearCache}
                  className="mt-4 w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors text-sm"
                >
                  Vider le cache
                </button>
              </div>

              {/* Conversation Statistics */}
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <MessageSquare className="text-blue-400" size={20} />
                  Conversations
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total (7 jours):</span>
                    <span className="font-semibold">{stats.conversation_statistics?.total_conversations || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Sessions uniques:</span>
                    <span className="font-semibold text-purple-400">{stats.conversation_statistics?.unique_sessions || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Complexité moyenne:</span>
                    <span className="font-semibold">{stats.conversation_statistics?.avg_complexity_score || 0}</span>
                  </div>
                </div>
              </div>

              {/* Model Distribution */}
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">🤖 Distribution des Modèles</h3>
                <div className="space-y-2 text-sm">
                  {stats.conversation_statistics?.model_distribution && Object.entries(stats.conversation_statistics.model_distribution).map(([model, count]) => (
                    <div key={model} className="flex justify-between items-center">
                      <span className="text-gray-400">{model.toUpperCase()}:</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-700 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${model === 'tfidf' ? 'bg-green-500' : 'bg-blue-500'}`}
                            style={{ width: `${(count / stats.conversation_statistics.total_conversations * 100)}%` }}
                          />
                        </div>
                        <span className="font-semibold w-12 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Category Distribution */}
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">📁 Top Catégories</h3>
                <div className="space-y-2 text-sm max-h-40 overflow-y-auto">
                  {stats.conversation_statistics?.category_distribution && Object.entries(stats.conversation_statistics.category_distribution)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 5)
                    .map(([category, count]) => (
                      <div key={category} className="flex justify-between">
                        <span className="text-gray-400 truncate">{category}:</span>
                        <span className="font-semibold ml-2">{count}</span>
                      </div>
                    ))}
                </div>
              </div>

              {/* Response Time */}
              {stats.conversation_statistics?.response_time && (
                <div className="bg-gray-800 rounded-lg p-4 md:col-span-2">
                  <h3 className="text-lg font-semibold mb-3">⏱️ Temps de Réponse</h3>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-gray-400 mb-1">Moyen</div>
                      <div className="text-2xl font-bold text-blue-400">
                        {stats.conversation_statistics.response_time.avg?.toFixed(2) || 'N/A'}s
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-400 mb-1">Min</div>
                      <div className="text-2xl font-bold text-green-400">
                        {stats.conversation_statistics.response_time.min?.toFixed(2) || 'N/A'}s
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-400 mb-1">Max</div>
                      <div className="text-2xl font-bold text-red-400">
                        {stats.conversation_statistics.response_time.max?.toFixed(2) || 'N/A'}s
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Configuration */}
              <div className="bg-gray-800 rounded-lg p-4 md:col-span-2">
                <h3 className="text-lg font-semibold mb-3">⚙️ Configuration</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Seuil de complexité:</span>
                    <span className="font-semibold">{stats.configuration?.complexity_threshold || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Cache activé:</span>
                    <span className={`font-semibold ${stats.configuration?.cache_enabled ? 'text-green-400' : 'text-red-400'}`}>
                      {stats.configuration?.cache_enabled ? 'Oui' : 'Non'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
