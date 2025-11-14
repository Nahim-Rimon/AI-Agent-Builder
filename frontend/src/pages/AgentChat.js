import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_BASE } from '../config';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AgentChat() {
  const { id } = useParams();
  const [msgs, setMsgs] = useState([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [agentInfo, setAgentInfo] = useState(null);
  const messagesEndRef = useRef(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
    fetchAgentInfo();
  }, [id, token]);

  useEffect(() => {
    scrollToBottom();
  }, [msgs]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchAgentInfo = async () => {
    try {
      const res = await axios.get(`${API_BASE}/agents/list`);
      const agent = res.data.find(a => a.id === parseInt(id));
      setAgentInfo(agent);
    } catch (err) {
      console.error('Failed to fetch agent info:', err);
    }
  };

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE}/chat/${id}/history`);
      setMsgs(res.data);
      setError('');
    } catch (err) {
      setError('Failed to load chat history: ' + (err.response?.data?.detail || err.message));
      if (err.response?.status === 404) {
        navigate('/');
      }
    } finally {
      setLoading(false);
    }
  };

  const send = async (e) => {
    e.preventDefault();
    if (!text.trim() || sending) return;

    const userMessage = text.trim();
    setText('');
    setSending(true);
    setError('');

    // Optimistically add user message
    const tempUserMsg = {
      id: Date.now(),
      sender: 'user',
      message: userMessage,
      created_at: new Date().toISOString()
    };
    setMsgs(prev => [...prev, tempUserMsg]);

    try {
      const res = await axios.post(`${API_BASE}/chat/${id}/send`, { message: userMessage });
      
      // Remove temp message and add real messages
      setMsgs(prev => {
        const filtered = prev.filter(m => m.id !== tempUserMsg.id);
        return [...filtered, 
          { id: res.data.user_message_id, sender: 'user', message: userMessage, created_at: new Date().toISOString() },
          { id: res.data.bot_message_id, sender: 'agent', message: res.data.response, created_at: new Date().toISOString() }
        ];
      });
    } catch (err) {
      setError('Send failed: ' + (err.response?.data?.detail || err.message));
      // Remove the optimistic message on error
      setMsgs(prev => prev.filter(m => m.id !== tempUserMsg.id));
      setText(userMessage); // Restore the text
    } finally {
      setSending(false);
    }
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading chat...</p>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div>
          <Link to="/" className="back-link">← Back to Dashboard</Link>
          <h2>{agentInfo?.name || 'Agent Chat'}</h2>
          {agentInfo?.role && <p className="chat-subtitle">{agentInfo.role}</p>}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="chat-messages">
        {msgs.length === 0 ? (
          <div className="empty-chat">
            <p>No messages yet. Start a conversation with your agent!</p>
          </div>
        ) : (
          msgs.map(msg => (
            <div
              key={msg.id}
              className={`message ${msg.sender === 'user' ? 'message-user' : 'message-agent'}`}
            >
              <div className="message-content">
                <div className="message-header">
                  <span className="message-sender">
                    {msg.sender === 'user' ? 'You' : agentInfo?.name || 'Agent'}
                  </span>
                  <span className="message-time">{formatTime(msg.created_at)}</span>
                </div>
                <div className="message-text">{msg.message}</div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={send}>
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Type your message..."
          rows="2"
          disabled={sending}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              send(e);
            }
          }}
        />
        <button type="submit" className="btn-primary" disabled={sending || !text.trim()}>
          {sending ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
