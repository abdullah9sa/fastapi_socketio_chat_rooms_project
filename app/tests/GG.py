import socketio

# Initialize the Socket.IO client
sio = socketio.AsyncClient()

# Define event handlers
@sio.on('connect')
async def on_connect():
    print('Connected to server')
    await sio.emit('join', {'message': 'Joined the chat'})

@sio.on('chat')
async def on_chat(data):
    print(f"Received chat message: {data['message']}")

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

# Connect to the Socket.IO server
async def start_client():
    await sio.connect('http://localhost:8000', namespaces=['/sockets'])

    while True:
        message = input("Enter a message to send: ")
        if message.lower() == 'exit':
            break
        await sio.emit('chat', {'message': message})

    await sio.disconnect()

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_client())
