import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim()) {
      navigate('/chat', { state: { username } });
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      backgroundColor: '#111b21',
      color: '#e9edef',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      padding: '16px',
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        backgroundColor: '#202c33',
        padding: '24px',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        margin: '0 16px'
      }}>
        <h1 style={{
          fontSize: '24px',
          fontWeight: '600',
          marginBottom: '20px',
          textAlign: 'center',
          letterSpacing: '-0.5px'
        }}>
          MeRadio
        </h1>
        
        <form onSubmit={handleSubmit} style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontSize: '14px',
              color: '#8696a0',
              fontWeight: '500'
            }}>
              Nombre de usuario
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: '#2a3942',
                color: '#e9edef',
                fontSize: '15px',
                outline: 'none',
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                letterSpacing: '-0.2px',
                boxSizing: 'border-box'
              }}
              placeholder="Ingresa tu nombre"
            />
          </div>
          
          <button
            type="submit"
            style={{
              width: '100%',
              padding: '12px 20px',
              backgroundColor: '#00a884',
              color: '#111b21',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '15px',
              opacity: username.trim() ? 1 : 0.5,
              transition: 'all 0.2s',
              letterSpacing: '-0.2px'
            }}
            disabled={!username.trim()}
          >
            Entrar al chat
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login; 