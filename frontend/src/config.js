export const CONFIG = {
  // Radio en metros
  CHAT_RADIUS: parseInt(process.env.REACT_APP_CHAT_RADIUS) || 1000, // 1km por defecto
  // MAP_RADIUS: 1000, // Si quieres un radio diferente para el mapa

  // Intervalos de tiempo en milisegundos
  LOCATION_UPDATE_INTERVAL: 10000, // 10 segundos

  // URL del WebSocket
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',

  // Colores
  COLORS: {
    USER_MESSAGE: '#005c4b', // Verde WhatsApp
    OTHER_MESSAGE: '#202c33', // Gris oscuro
    CONNECTED: '#00a884', // Verde claro
    DISCONNECTED: '#8696a0', // Gris azulado
  }
}; 