import React, { useState, useEffect, useRef } from 'react';
import { Send, Plus, Menu, MessageSquare, Trash2, Edit2 } from 'lucide-react';

export default function ChatInterface() {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
    if (currentConvId === id) {
      if (updated.length > 0) {
        loadConversation(updated[0].id);
      } else {
        createNewConversation();
      }
    }
  };

  const updateConversationTitle = (id, firstMessage) => {
    const updated = conversations.map(c => {
      if (c.id === id && c.title === 'Nouvelle conversation') {
        return { ...c, title: firstMessage.substring(0, 50) };
      }
      return c;
    });
    setConversations(updated);
    saveConversations(updated);
  };

  const updateConversationMessages = (newMessages) => {
    const updated = conversations.map(c => {
      if (c.id === currentConvId) {
        return { ...c, messages: newMessages };
      }
      return c;
    });
    setConversations(updated);
    saveConversations(updated);
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    if (messages.length === 0) {
      updateConversationTitle(currentConvId, input);
    }

    try {
      // Appeler l'agent IA local
      const response = await fetch('http://localhost:8002/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: input
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      
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
        content: responseText,
        timestamp: new Date().toISOString()
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);
      updateConversationMessages(finalMessages);
    } catch (error) {
      console.error('Erreur:', error);
      const errorMessage = {
        role: 'assistant',
        content: `❌ Désolé, une erreur s'est produite lors de la classification.\n\nErreur: ${error.message}\n\nAssurez-vous que l'agent IA est démarré (http://localhost:8002)`,
        timestamp: new Date().toISOString()
      };
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      updateConversationMessages(finalMessages);
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
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-2xl px-4">
                <h2 className="text-4xl font-bold mb-4">🤖 Agent IA Intelligent</h2>
                <p className="text-gray-400 text-lg mb-6">Classificateur de tickets du centre d'appels</p>
                <div className="text-left bg-gray-800 rounded-lg p-6 space-y-3">
                  <p className="text-gray-300 font-semibold">Comment ça marche ?</p>
                  <ul className="text-gray-400 space-y-2 text-sm">
                    <li>📝 Décrivez votre problème ou ticket</li>
                    <li>🧠 L'agent analyse la complexité de votre texte</li>
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
    </div>
  );
}
