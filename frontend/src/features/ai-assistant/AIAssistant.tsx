import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, Clock, BarChart } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useAIChat } from './hooks/useAI';
import { Loader2 } from 'lucide-react';

export function AIAssistant() {
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: "Hello! I'm your Smart Analytics Assistant. I can help generate revision plans, summarize complex student trends, or analyze engagement metrics. What do you need help with today?" }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const chatMutation = useAIChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const suggestions = [
    { icon: BookOpen, text: "Generate an intervention plan for Fraction Division" },
    { icon: Clock, text: "Which students need immediate attention?" },
    { icon: BarChart, text: "Summarize last week's engagement trends" }
  ];

  const handleSend = async (text: string) => {
    if (!text.trim() || chatMutation.isPending) return;
    
    // Optimistic UI update
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text }]);
    setInput('');
    
    try {
      const response = await chatMutation.mutateAsync({ query: text });
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        role: 'assistant', 
        text: response.answer
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        role: 'assistant', 
        text: "I'm sorry, I encountered an error while processing your request. Please try again."
      }]);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto border rounded-2xl bg-white shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 p-4 border-b bg-gray-50/50">
        <div className="bg-primary/10 p-2 rounded-lg">
          <Sparkles className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="font-semibold">EduSense Smart Assistant</h2>
          <p className="text-xs text-muted-foreground">Powered by EduSense Analytics Engine</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-secondary/10 text-secondary'}`}>
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-tr-sm' : 'bg-gray-100 text-gray-900 rounded-tl-sm'}`}>
              {msg.text}
            </div>
          </div>
        ))}

        {messages.length === 1 && (
          <div className="pt-8">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-1">Suggested Prompts</p>
            <div className="grid sm:grid-cols-2 gap-3">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(s.text)}
                  className="flex items-center gap-3 p-3 rounded-xl border bg-white hover:border-primary/50 hover:bg-primary/5 transition-all text-left text-sm"
                >
                  <div className="bg-gray-100 p-2 rounded-lg text-gray-600">
                    <s.icon className="w-4 h-4" />
                  </div>
                  <span className="text-gray-700 font-medium">{s.text}</span>
                </button>
              ))}
            </div>
          </div>
        )}
        
        {chatMutation.isPending && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-secondary/10 text-secondary">
              <Bot className="w-4 h-4" />
            </div>
            <div className="max-w-[80%] rounded-2xl px-4 py-3 text-sm bg-gray-100 text-gray-900 rounded-tl-sm flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
              <span className="text-gray-500">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t bg-white">
        <div className="relative flex items-center">
          <Input 
            value={input}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
            onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && handleSend(input)}
            placeholder="Ask anything about student performance or trends..."
            className="pr-12 py-6 rounded-full bg-gray-50 border-gray-200 focus:bg-white text-base"
          />
          <Button 
            size="icon" 
            className="absolute right-2 rounded-full h-10 w-10"
            onClick={() => handleSend(input)}
            disabled={!input.trim() || chatMutation.isPending}
          >
            {chatMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
