

import socketio

# Create a Socket.IO client instance
sio = socketio.Client()

@sio.on("connect")
def on_connect():
    print("Connected to Socket.IO server")

@sio.on("new_message")
def on_new_message(data):
    print("New message received:", data)

@sio.on("disconnect")
def on_disconnect():
    print("Disconnected from Socket.IO server")

if __name__ == "__main__":
    # Change the URL to match your server's URL
    server_url = "http://localhost:8000/"
    
    # Connect to the Socket.IO server
    sio.connect(server_url)
    
    try:
        # Keep the script running to listen for events
        sio.wait()
    except KeyboardInterrupt:
        # Disconnect when the script is interrupted
        sio.disconnect()


# import socketio

# # Create a SocketIO client instance
# sio = socketio.Client()

# # Event handler for when a new message is received
# @sio.on('new_message')
# def on_new_message(data):
#     print('New Message:', data)

# # Event handler for successful connection
# @sio.on('connect')
# def on_connect():
#     print('Connected to server')

# # Event handler for disconnection
# @sio.on('disconnect')
# def on_disconnect():
#     print('Disconnected from server')

# # Connect to the SocketIO FastAPI server
# sio.connect('http://127.0.0.1:8001/socket.io')

# try:
#     while True:
#         pass  # Keep the script running to receive events
# except KeyboardInterrupt:
#     # Disconnect gracefully on Ctrl+C
#     sio.disconnect()
