from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from geopy.distance import geodesic
import asyncio
from typing import Dict, List, Optional, Callable
from colorama import init, Fore, Back, Style
import pprint
from datetime import datetime
from config import Config

# Initialize colorama
init()

# Pretty printer for JSON
pp = pprint.PrettyPrinter(indent=2)

def log_message(message_type: str, data: dict):
    """Log a message with color and formatting"""
    print(f"\n{Fore.CYAN}=== {message_type} ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Message data:{Style.RESET_ALL}")
    pp.pprint(data)
    print(f"{Fore.CYAN}=== End {message_type} ==={Style.RESET_ALL}\n")

def log_error(error_type: str, error: str):
    """Log an error with color"""
    print(f"\n{Fore.RED}ERROR: {error_type}{Style.RESET_ALL}")
    print(f"{Fore.RED}Details: {error}{Style.RESET_ALL}\n")

def log_success(message: str):
    """Log a success message with color"""
    print(f"\n{Fore.GREEN}SUCCESS: {message}{Style.RESET_ALL}\n")

def log_info(message: str):
    """Log an info message with color"""
    print(f"\n{Fore.BLUE}INFO: {message}{Style.RESET_ALL}\n")

app = FastAPI()

# CORS middleware with WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
RADIUS_KM = Config.CHAT_RADIUS / 1000  # Convertir metros a kilómetros

# Store active connections
active_connections: Dict[str, WebSocket] = {}
user_locations: Dict[str, dict] = {}
user_messages: Dict[str, List[dict]] = {}

def get_users_in_range(lat: float, lon: float, exclude_client_id: str = None) -> List[dict]:
    users_in_range = []
    log_info(f"Calculating users in range for position: {lat}, {lon}")
    
    for client_id, location in user_locations.items():
        # Excluir al usuario que envía la ubicación
        if exclude_client_id and client_id == exclude_client_id:
            continue
            
        distance = geodesic((lat, lon), (location['lat'], location['lon'])).kilometers
        if distance <= RADIUS_KM:
            users_in_range.append({
                'client_id': client_id,
                'username': location['username'],
                'lat': location['lat'],
                'lon': location['lon']
            })
    
    log_success(f"Found {len(users_in_range)} users in range")
    return users_in_range

async def handle_connect(websocket: WebSocket, message: dict) -> str:
    """Handle initial connection"""
    username = message.get('username')
    lat = message.get('lat')
    lon = message.get('lon')
    
    if not all([username, lat, lon]):
        log_error("Invalid connect", f"Missing required fields: username, lat, lon")
        await websocket.send_json({
            'type': 'error',
            'message': 'Missing required fields: username, lat, lon'
        })
        return None
    
    log_info(f"Handling connection for user {username}")
    log_message("Connection", message)
    
    # Buscar si ya existe un client_id para este username
    client_id = None
    for cid, user_data in user_locations.items():
        if user_data['username'] == username:
            client_id = cid
            break
    
    # Si no existe, crear uno nuevo
    if not client_id:
        client_id = str(uuid.uuid4())
        log_success(f"Created new client_id {client_id} for user {username}")
    else:
        log_info(f"Reusing existing client_id {client_id} for user {username}")
    
    # Guardar la conexión y la información del usuario
    active_connections[client_id] = websocket
    user_locations[client_id] = {
        'username': username,
        'lat': lat,
        'lon': lon
    }
    
    log_info(f"Stored connection in active_connections: {client_id}")
    log_info(f"Current active connections: {list(active_connections.keys())}")
    
    try:
        # Enviar confirmación con el client_id
        await websocket.send_json({
            'type': 'connected',
            'client_id': client_id
        })
        log_success(f"User {username} connected with client_id {client_id}")
        return client_id
    except Exception as e:
        log_error("Send connected message", str(e))
        if client_id in active_connections:
            del active_connections[client_id]
        if client_id in user_locations:
            del user_locations[client_id]
        return None

async def handle_update_user(websocket: WebSocket, message: dict) -> None:
    """Handle user updates (position or username)"""
    client_id = message.get('client_id')
    if not client_id:
        await websocket.send_json({
            'type': 'error',
            'message': 'Missing client_id'
        })
        return

    print(f"Updating user {client_id} with new data:", message)
    
    if client_id in user_locations:
        user_locations[client_id].update({
            'username': message['username'],
            'lat': message['lat'],
            'lon': message['lon']
        })
        
        # Send updated users in range
        users_in_range = get_users_in_range(message['lat'], message['lon'])
        await websocket.send_json({
            'type': 'users_in_range',
            'users': users_in_range
        })

async def handle_sent_location(websocket: WebSocket, message: dict) -> None:
    """Handle location updates"""
    client_id = message.get('client_id')
    if not client_id:
        log_error("Missing client_id", "Location update without client_id")
        await websocket.send_json({
            'type': 'error',
            'message': 'Missing client_id'
        })
        return

    log_message("Location Update", message)
    
    # Update user location
    if client_id not in user_locations:
        log_info(f"Creating new location entry for client {client_id}")
        user_locations[client_id] = {
            'username': 'Unknown',  # Default username if not set
            'lat': message['lat'],
            'lon': message['lon']
        }
    else:
        log_info(f"Updating location for client {client_id}")
        user_locations[client_id].update({
            'lat': message['lat'],
            'lon': message['lon']
        })
    
    # Send updated users in range (excluyendo al usuario que envía la ubicación)
    users_in_range = get_users_in_range(message['lat'], message['lon'], exclude_client_id=client_id)
    log_info(f"Users in range for {client_id}: {len(users_in_range)} users")
    
    await websocket.send_json({
        'type': 'users_in_range',
        'users': users_in_range
    })

async def handle_sent_message(websocket: WebSocket, message: dict) -> None:
    """Handle new message"""
    client_id = message.get('client_id')
    if not client_id:
        log_error("Missing client_id", "Message without client_id")
        await websocket.send_json({
            'type': 'error',
            'message': 'Missing client_id'
        })
        return

    if client_id not in user_locations:
        log_error("Client not found", f"Client {client_id} not found in user_locations")
        await websocket.send_json({
            'type': 'error',
            'message': 'Client not found'
        })
        return

    log_message("New Message", message)
    message_data = {
        'client_id': client_id,
        'username': user_locations[client_id]['username'],
        'content': message['content'],
        'lat': message['lat'],
        'lon': message['lon'],
        'timestamp': int(datetime.now().timestamp() * 1000)  # Timestamp en milisegundos
    }
    
    # Add to message history
    if client_id not in user_messages:
        user_messages[client_id] = []
    user_messages[client_id].append(message_data)
    log_success(f"Added message to history for client {client_id}")
    
    # Broadcast to users in range (except the sender)
    broadcast_count = 0
    for user_id, user_loc in user_locations.items():
        # Skip the sender
        if user_id == client_id:
            continue
            
        distance = geodesic(
            (message['lat'], message['lon']),
            (user_loc['lat'], user_loc['lon'])
        ).kilometers
        
        if distance <= RADIUS_KM and user_id in active_connections:
            broadcast_count += 1
            await active_connections[user_id].send_json({
                'type': 'new_message',
                'message': message_data
            })
    log_info(f"Broadcasted message to {broadcast_count} users in range")

async def handle_get_history_messages(websocket: WebSocket, message: dict) -> None:
    """Handle message history request"""
    client_id = message.get('client_id')
    if not client_id:
        log_error("Missing client_id", "History request without client_id")
        await websocket.send_json({
            'type': 'error',
            'message': 'Missing client_id'
        })
        return

    log_message("History Request", message)
    messages = []
    for msg_list in user_messages.values():
        for msg in msg_list:
            distance = geodesic(
                (message['lat'], message['lon']),
                (msg['lat'], msg['lon'])
            ).kilometers
            if distance <= RADIUS_KM:
                messages.append(msg)
    
    log_info(f"Sending {len(messages)} messages in history")
    await websocket.send_json({
        'type': 'messages_history',
        'messages': messages
    })

async def handle_disconnect(websocket: WebSocket, message: dict) -> None:
    """Handle client disconnect message"""
    client_id = message.get('client_id')
    if not client_id:
        log_error("Missing client_id", "Disconnect without client_id")
        return

    log_info(f"Received disconnect message from client {client_id}")
    
    # Solo eliminar la conexión y la ubicación, pero mantener los mensajes
    if client_id in active_connections:
        del active_connections[client_id]
        log_info(f"Removed client {client_id} from active_connections")
    if client_id in user_locations:
        del user_locations[client_id]
        log_info(f"Removed client {client_id} from user_locations")
    
    log_info(f"Current active connections: {list(active_connections.keys())}")
    log_info(f"Current user locations: {list(user_locations.keys())}")

# Message type handlers
message_handlers: Dict[str, Callable] = {
    'connect': handle_connect,
    'update_user': handle_update_user,
    'sent_location': handle_sent_location,
    'get_history_messages': handle_get_history_messages,
    'sent_message': handle_sent_message,
    'disconnect': handle_disconnect,
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = None
    username = None
    position = None

    try:
        await websocket.accept()
        log_info("WebSocket connection accepted")

        while True:
            try:
                data = await websocket.receive_json()
                log_message("Received", data)

                handler = message_handlers.get(data["type"])
                if handler:
                    await handler(websocket, data)
                else:
                    log_error("Unknown message type", f"Unknown message type: {data['type']}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {data['type']}"
                    })

            except WebSocketDisconnect:
                log_info(f"Client {client_id} disconnected")
                break
            except Exception as e:
                log_error("Processing error", str(e))
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                break

    except Exception as e:
        log_error("WebSocket error", str(e))
    finally:
        if client_id:
            log_info(f"Cleaning up client {client_id}")
            if client_id in active_connections:
                del active_connections[client_id]
            if client_id in user_locations:
                del user_locations[client_id]
            log_info(f"Active connections: {list(active_connections.keys())}")
            log_info(f"User locations: {list(user_locations.keys())}") 