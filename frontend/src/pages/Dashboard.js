import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE } from '../config';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: '',
    role: '',
    goal: '',
    model_name: 'gpt-4-turbo',
    temperature: 0.7,
    max_tokens: 1024,
    top_p: 1.0,
    top_k: 50,
    api_key: '',
    provider: 'openai'
  });
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
  }, [token]);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE}/agents/list`);
      setAgents(res.data);
      setError('');
    } catch (err) {
      setError('Failed to load agents: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const create = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('Agent name is required');
      return;
    }

    if (!form.api_key.trim()) {
      setError('An API key is required for the selected model.');
      return;
    }
    
    setCreating(true);
    setError('');
    
    try {
      await axios.post(`${API_BASE}/agents/create`, form);
      setForm({ name: '', role: '', goal: '', model_name: 'gpt-4-turbo', temperature: 0.7, max_tokens: 1024, top_p: 1.0, top_k: 50, api_key: '', provider: 'openai' });
      setShowForm(false);
      fetchAgents();
    } catch (err) {
      setError('Create failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setCreating(false);
    }
  };

  const deleteAgent = async (agentId) => {
    if (!window.confirm('Are you sure you want to delete this agent? This will also delete all chat history.')) {
      return;
    }
    
    try {
      await axios.delete(`${API_BASE}/agents/${agentId}`);
      fetchAgents();
    } catch (err) {
      setError('Delete failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading agents...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>AI Agents</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Create Agent'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <div className="card agent-form-card">
          <h3>Create New Agent</h3>
          <form onSubmit={create}>
            <div className="form-group">
              <label>Name *</label>
              <input
                placeholder="Agent name"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Role</label>
              <input
                placeholder="e.g., Research Assistant, Customer Support"
                value={form.role}
                onChange={e => setForm({ ...form, role: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Goal</label>
              <textarea
                placeholder="What should this agent help with?"
                value={form.goal}
                onChange={e => setForm({ ...form, goal: e.target.value })}
                rows="3"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Model</label>
                <input
                  type="text"
                  placeholder="e.g., gpt-4o, gemini-2.0-flash, llama-3-70b"
                  list="model-options"
                  value={form.model_name}
                  onChange={e => setForm({ ...form, model_name: e.target.value })}
                />
                <datalist id="model-options">
                  <option value="gpt-4-turbo" />
                  <option value="gpt-4o" />
                  <option value="gpt-4.1" />
                  <option value="gpt-3.5-turbo" />
                  <option value="gpt-3.5-turbo-16k" />
                  <option value="claude-3.5-sonnet" />
                  <option value="gemini-2.0-pro" />
                  <option value="gemini-2.0-flash" />
                  <option value="gemini-1.5-pro" />
                  <option value="llama-3-70b" />
                  <option value="llama-3-8b" />
                  <option value="fireworks-gpt-4o-mini" />
                </datalist>
                <small>Type any model identifier supported by your provider.</small>
              </div>

              <div className="form-group">
                <label>Provider</label>
                <select
                  value={form.provider}
                  onChange={e => setForm({ ...form, provider: e.target.value })}
                >
                  <option value="openai">OpenAI / Azure OpenAI</option>
                  <option value="gemini">Google Gemini</option>
                  <option value="fireworks">Fireworks.ai</option>
                </select>
                <small>Currently supported providers.</small>
              </div>

              <div className="form-group">
                <label>Temperature: {form.temperature}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={form.temperature}
                  onChange={e => setForm({ ...form, temperature: parseFloat(e.target.value) })}
                />
                <small>Controls randomness (0 = deterministic, 1 = creative)</small>
              </div>

              <div className="form-group">
                <label>Top P: {form.top_p}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={form.top_p}
                  onChange={e => setForm({ ...form, top_p: parseFloat(e.target.value) })}
                />
                <small>Nucleus sampling: consider tokens with top_p probability mass</small>
              </div>

              <div className="form-group">
                <label>Top K: {form.top_k}</label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  step="1"
                  value={form.top_k}
                  onChange={e => setForm({ ...form, top_k: parseInt(e.target.value) })}
                />
                <small>Consider only top K most likely tokens</small>
              </div>

              <div className="form-group">
                <label>Max Tokens</label>
                <input
                  type="number"
                  min="100"
                  max="4096"
                  value={form.max_tokens}
                  onChange={e => setForm({ ...form, max_tokens: parseInt(e.target.value) })}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Provider API Key *</label>
              <input
                type="password"
                placeholder="sk-***************************"
                value={form.api_key}
                onChange={e => setForm({ ...form, api_key: e.target.value })}
                autoComplete="off"
                required
              />
              <small>Stored securely and sent only to your provider for this agent.</small>
            </div>

            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? 'Creating...' : 'Create Agent'}
            </button>
          </form>
        </div>
      )}

      {agents.length === 0 ? (
        <div className="empty-state">
          <p>No agents yet. Create your first agent to get started!</p>
        </div>
      ) : (
        <div className="agents-grid">
          {agents.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="agent-card-header">
                <h3>{agent.name}</h3>
                <button
                  className="btn-icon"
                  onClick={() => deleteAgent(agent.id)}
                  title="Delete agent"
                >
                  ×
                </button>
              </div>
              
              {agent.role && <p className="agent-role">{agent.role}</p>}
              {agent.goal && <p className="agent-goal">{agent.goal}</p>}
              
              <div className="agent-meta">
                <span className="badge">{agent.model_name}</span>
                <span className="badge">Provider: {agent.provider || 'openai'}</span>
                <span className="badge">Temp: {agent.temperature}</span>
                <span className="badge">Max: {agent.max_tokens}</span>
              </div>
              
              <Link to={`/agent/${agent.id}`} className="btn-secondary">
                Open Chat →
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
