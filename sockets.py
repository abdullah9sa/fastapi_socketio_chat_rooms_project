'''

this file should have validation for before making a room channel,
refusing the connection if there is no room by the given room id. and same for user.
like this:
    try:
        room = await Room.get(id=room_id)
    except Room.DoesNotExist:
        raise HTTPException(status_code=404, detail="Room not found")

*not implemented because of time

'''


import socketio
import jwt
from fastapi.security import OAuth2PasswordBearer
from app.models.room import Room
from app.models.user import User


room_sockets = {}

sio_server = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])

SECRET_KEY = "your-secret-key"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate(environ, auth):
    print("Authinticating ...")

    jwt_token = auth.get('token')#environ.get("QUERY_STRING", "").replace("token=", "")
    # Verify JWT token and get user_id
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except jwt.ExpiredSignatureError:
        # raise socketio.exceptions.ConnectionRefusedError("JWT token expired")
        print("JWT token expired")
        return None
    except jwt.DecodeError:
        # raise socketio.exceptions.ConnectionRefusedError("Invalid JWT token")
        print("Invalid JWT token")
        return None

    print("username")
    print(user_id)
    user = await User.get_or_none(username=user_id)

    # Your authentication logic using the user object
    is_authenticated = True  # Replace this with your actual authentication logic

    if not is_authenticated:
        return None
        raise socketio.exceptions.ConnectionRefusedError("Authentication failed")
    
    print("auth seccesfuly")
    return user
    
sio_server.on("connect")(authenticate)
class ConnectionRefusedException(Exception):
    pass

@sio_server.event
async def connect(sid, environ, auth):
    user = await authenticate(environ, auth)
    room_id = auth.get('room_id')
    if user:
        user_id = user.id
    else:
        print("Connection failed: Authentication error")
        raise ConnectionRefusedException("Authentication failed")

    
    room = await Room.filter(id=room_id).prefetch_related('users').first()

    if room:
        print("Room users:")
        for user in room.users:
            print(user)  # Access the user's attribute, e.g., username

        if user_id not in [user.id for user in room.users]:
            print("User is not in the room")
            raise ConnectionRefusedException("User is not in the room")

    else:
        print("Room not found")
        raise ConnectionRefusedException("Room not found")

    
    room_sid = f'{room_id}_{user_id}'  
    sio_server.enter_room(sid, room_sid)  # Join the room
    room_sockets[room_sid] = sid
    print(f'{sid}: connected to room {room_id} as user {user_id}')


@sio_server.event
async def chat(sid, data):
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    message = data.get('message')
    room_sid = f'{room_id}_{user_id}'
    if room_sid in room_sockets:
        await sio_server.emit('chat', {'user_id': user_id, 'message': message}, room=room_sid)

@sio_server.event
async def disconnect(sid):
    room_sid = next((room_sid for room_sid, s in room_sockets.items() if s == sid), None)
    if room_sid:
        del room_sockets[room_sid]
        print(f'{sid}: disconnected')

async def send_message_to_channel(user_id,message_data,room_sid):
    await sio_server.emit("chat", {
        "user_id": user_id,
        "message": message_data#.text
    }, room=room_sid)


sio_app = socketio.ASGIApp(socketio_server=sio_server, socketio_path='sockets')
