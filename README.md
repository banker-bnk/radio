# MeRadio - Chat de Proximidad

MeRadio es una aplicación de chat en tiempo real que permite a los usuarios comunicarse con otros que se encuentren dentro de un radio de 1 kilómetro. La aplicación utiliza la geolocalización para mostrar mensajes y usuarios cercanos, con una interfaz moderna y responsive inspirada en WhatsApp.

## Características

- Chat en tiempo real con usuarios cercanos
- Geolocalización en tiempo real
- Radio de alcance de 1 kilómetro
- Interfaz moderna tipo WhatsApp
- Modo oscuro
- Diseño responsive para móviles
- Indicadores de estado de conexión
- Mapa interactivo de usuarios cercanos

## Requisitos del Sistema

- Python 3.8 o superior
- Node.js 14 o superior
- npm 6 o superior
- Navegador web moderno con soporte para WebSocket y geolocalización

## Instalación

### Backend

1. Navega al directorio del backend:
   ```bash
   cd backend
   ```

2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   Crea un archivo `.env` en el directorio `backend` con:
   ```
   CHAT_RADIUS=1000
   HOST=0.0.0.0
   PORT=8000
   WS_URL=ws://localhost:8000/ws
   ```

### Frontend

1. Navega al directorio del frontend:
   ```bash
   cd frontend
   ```

2. Instala las dependencias:
   ```bash
   npm install
   ```

3. Configura las variables de entorno:
   Crea un archivo `.env` en el directorio `frontend` con:
   ```
   REACT_APP_WS_URL=ws://localhost:8000/ws
   ```

## Uso

1. Inicia el backend:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. Inicia el frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Abre tu navegador en `http://localhost:3000`

## Estructura del Proyecto

```
meradio/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Chat.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── .env
└── README.md
```

## Contribución

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Pablo Kere - [@pablokere](https://github.com/pablokere)

Link del Proyecto: [https://github.com/pablokere/meradio](https://github.com/pablokere/meradio)
