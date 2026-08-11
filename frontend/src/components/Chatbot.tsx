import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../api';
import type { ChatMessage } from '../types';

const QUICK_QUESTIONS = [
  'Wilayah mana yang paling cocok untuk usaha kuliner?',
  'Saya punya budget 500 juta, daerah mana yang terjangkau?',
  'Bandingkan Kota Surabaya vs Kota Semarang',
  'Top 5 wilayah dengan pertumbuhan tertinggi?',
  'Wilayah mana yang risikonya paling rendah?',
];

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Halo! 👋 Saya **ProspekJawa AI**, konsultan investasi Anda untuk wilayah Pulau Jawa.\n\nSaya memiliki data 119 kota/kabupaten di 6 provinsi. Tanya saya apa saja tentang investasi, properti, atau potensi wilayah!',
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen) inputRef.current?.focus();
  }, [isOpen]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: text.trim(), timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage(text.trim(), sessionId);
      setSessionId(res.session_id);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.response,
        timestamp: Date.now(),
      }]);
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ Maaf, terjadi kesalahan: ${e.message || 'Coba lagi nanti.'}`,
        timestamp: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const formatContent = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <>
      {/* FAB Button */}
      <button
        className={`chatbot-fab ${isOpen ? 'chatbot-fab-active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="AI Konsultan Investasi"
        id="chatbot-toggle"
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="chatbot-panel">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-info">
              <div className="chatbot-avatar">🤖</div>
              <div>
                <div className="chatbot-header-title">ProspekJawa AI</div>
                <div className="chatbot-header-sub">Konsultan Investasi Wilayah</div>
              </div>
            </div>
            <button className="chatbot-close" onClick={() => setIsOpen(false)}>✕</button>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chatbot-msg chatbot-msg-${msg.role}`}>
                {msg.role === 'assistant' && <div className="chatbot-msg-avatar">🤖</div>}
                <div
                  className={`chatbot-msg-bubble chatbot-msg-bubble-${msg.role}`}
                  dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
                />
              </div>
            ))}

            {loading && (
              <div className="chatbot-msg chatbot-msg-assistant">
                <div className="chatbot-msg-avatar">🤖</div>
                <div className="chatbot-msg-bubble chatbot-msg-bubble-assistant">
                  <div className="chatbot-typing">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Questions (only show at start) */}
            {messages.length <= 1 && !loading && (
              <div className="chatbot-quick">
                <p className="chatbot-quick-label">Contoh pertanyaan:</p>
                {QUICK_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    className="chatbot-quick-btn"
                    onClick={() => sendMessage(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form className="chatbot-input-form" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              type="text"
              className="chatbot-input"
              placeholder="Tanyakan tentang investasi di Jawa..."
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
              id="chatbot-input"
            />
            <button
              type="submit"
              className="chatbot-send"
              disabled={!input.trim() || loading}
              id="chatbot-send"
            >
              ➤
            </button>
          </form>
        </div>
      )}
    </>
  );
}
