'''

TASK7: Abdullah Salih.
same as task 5 but added 
- indexing for room and Chat_Messege models
- caching for the  chat_history route, use aiocache for caching, due to package confilct betwwen redis and socketio, short time to resolve the confilc so used another caching package
- pagination based on user input

'''
from fastapi import FastAPI
from app.dependencies.database import init_tortoise, close_tortoise
from fastapi.middleware.cors import CORSMiddleware
from app.models.chat_messege import Chat_Messege
from sockets import sio_app
from app.routes import chat_routes
from app.routes import user_routes
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI


app = FastAPI()



# Add CORS middleware for handling Cross-Origin requests
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])

origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_db():
    await init_tortoise(app)

@app.on_event("shutdown")
async def shutdown_db():

    await close_tortoise(app)


app.mount('/', app=sio_app)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000,reload=True)
