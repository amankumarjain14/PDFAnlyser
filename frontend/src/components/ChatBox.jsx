import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import { chatWithPDF } from '../services/api';
import styles from './ChatBox.module.css';

const ChatBox = ({ jobId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const res = await chatWithPDF(jobId, newMessages);
      setMessages([...newMessages, { role: 'assistant', content: res.data.answer }]);
    } catch (err) {
      console.error('Chat error', err);
      setMessages([...newMessages, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <Bot size={18} className={styles.botIcon} />
        <h3>Chat with PDF</h3>
      </div>
      
      <div className={styles.messagesList} ref={scrollRef}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <p>Ask anything about the document. I have the full context!</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`${styles.messageWrapper} ${msg.role === 'user' ? styles.user : styles.bot}`}>
            <div className={styles.avatar}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className={styles.messageContent}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className={`${styles.messageWrapper} ${styles.bot}`}>
            <div className={styles.avatar}><Bot size={14} /></div>
            <div className={`${styles.messageContent} ${styles.loading}`}>
              <Loader2 size={16} className={styles.spin} />
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form className={styles.inputArea} onSubmit={handleSend}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={isLoading}
        />
        <button type="submit" disabled={!input.trim() || isLoading}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
