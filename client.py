# client.py

import asyncio
import socketio

sio_client = socketio.AsyncClient()

@sio_client.event
async def connect():
    print('I\'m connected')

@sio_client.event
async def disconnect():
    print('I\'m disconnected')

@sio_client.event
async def chat(data):
    user_id = data.get('user_id')
    message = data.get('message')
    print(f'Received a chat message from user {user_id}: {message}')

async def main():
    user_id = 1  # Replace with the actual user ID
    room_id = 1  # Replace with the actual room ID
    auth = {'user_id': user_id, 'room_id': room_id}
    await sio_client.connect(url=f'http://localhost:8000', socketio_path='sockets', auth=auth)
    await asyncio.sleep(60)  # Keep the client connected for 60 seconds
    await sio_client.disconnect()

asyncio.run(main())
