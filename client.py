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
    #token generated from /token route
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYmR1bGxhaCIsImV4cCI6MTY5MzA1NTI4NX0.gOPQgIHEG55ytUKJm-cEHW-VrcXFQV5rgKX_G6vjYQs" 
    room_id = 1  # room id
    auth = {'token': token, 'room_id': room_id}
    await sio_client.connect(url=f'http://localhost:8000', socketio_path='sockets', auth=auth)
    await asyncio.sleep(60)  # Keep the client connected for 60 seconds
    await sio_client.disconnect()

asyncio.run(main())
