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

room_sockets = {}

sio_server = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=[])

@sio_server.event
async def connect(sid, environ, auth):
    room_id = auth.get('room_id')
    user_id = auth.get('user_id')
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
