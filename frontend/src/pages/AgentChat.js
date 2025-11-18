import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_BASE } from '../config';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function AgentChat() {
  const { id } = useParams();
  const [msgs, setMsgs] = useState([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [agentInfo, setAgentInfo] = useState(null);
  const [waitingForResponse, setWaitingForResponse] = useState(false);
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
    setWaitingForResponse(true);

    // Optimistically add user message
    const tempUserMsg = {
      id: Date.now(),
      sender: 'user',
      message: userMessage,
      created_at: new Date().toISOString()
    };
    setMsgs(prev => [...prev, tempUserMsg]);

    try {
      const response = await fetch(`${API_BASE}/chat/${id}/send-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let userMessageId = null;
      let botMessageId = null;
      let accumulatedResponse = '';
      let tempAgentMsgId = null;
      let firstChunk = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'start') {
                userMessageId = data.user_message_id;
                // Replace temp user message with real one
                setMsgs(prev => {
                  const filtered = prev.filter(m => m.id !== tempUserMsg.id);
                  return [...filtered, 
                    { id: userMessageId, sender: 'user', message: userMessage, created_at: new Date().toISOString() }
                  ];
                });
              } else if (data.type === 'chunk') {
                accumulatedResponse += data.content;
                setWaitingForResponse(false);
                // Create agent message on first chunk
                if (firstChunk) {
                  firstChunk = false;
                  tempAgentMsgId = Date.now();
                  setMsgs(prev => [...prev, {
                    id: tempAgentMsgId,
                    sender: 'agent',
                    message: accumulatedResponse,
                    created_at: new Date().toISOString(),
                    isStreaming: true
                  }]);
                } else {
                  // Update the streaming message
                  setMsgs(prev => prev.map(msg => 
                    msg.id === tempAgentMsgId 
                      ? { ...msg, message: accumulatedResponse, isStreaming: true }
                      : msg
                  ));
                }
              } else if (data.type === 'done') {
                botMessageId = data.bot_message_id;
                // Replace temp agent message with final one (remove isStreaming)
                setMsgs(prev => prev.map(msg => 
                  msg.id === tempAgentMsgId 
                    ? { id: botMessageId, sender: 'agent', message: data.full_response, created_at: new Date().toISOString() }
                    : msg
                ));
              } else if (data.type === 'error') {
                throw new Error(data.message);
              }
            } catch (parseErr) {
              console.error('Error parsing SSE data:', parseErr);
            }
          }
        }
      }
    } catch (err) {
      setError('Send failed: ' + (err.message || 'Unknown error'));
      // Remove the optimistic messages on error
      setMsgs(prev => {
        let filtered = prev.filter(m => m.id !== tempUserMsg.id);
        if (tempAgentMsgId) {
          filtered = filtered.filter(m => m.id !== tempAgentMsgId);
        }
        return filtered;
      });
      setText(userMessage); // Restore the text
    } finally {
      setSending(false);
      setWaitingForResponse(false);
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
                <div className="message-text">
                  {msg.sender === 'agent' ? (
                    msg.isStreaming && msg.message ? (
                      <>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.message}
                        </ReactMarkdown>
                        <span className="streaming-cursor">▊</span>
                      </>
                    ) : msg.message ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.message}
                      </ReactMarkdown>
                    ) : null
                  ) : (
                    msg.message
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        {waitingForResponse && (
          <div className="message message-agent">
            <div className="message-content">
              <div className="message-header">
                <span className="message-sender">
                  {agentInfo?.name || 'Agent'}
                </span>
                <span className="message-time">{formatTime(new Date().toISOString())}</span>
              </div>
              <div className="message-text">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
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
