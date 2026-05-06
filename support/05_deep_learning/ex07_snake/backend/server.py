import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from typing import List
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self): self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections: self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:
            try: await connection.send_text(message)
            except: self.disconnect(connection)

manager = ConnectionManager()

class SnakeGame:
    def __init__(self, size=10):
        self.size = size; self.reset()
    def reset(self):
        self.snake = [[self.size // 2, self.size // 2]]
        self.spawn_food()
    def spawn_food(self):
        while True:
            self.food = [np.random.randint(0, self.size), np.random.randint(0, self.size)]
            if self.food not in self.snake: break
    def step(self, action: int):
        head = self.snake[0]
        if action == 0: new_head = [head[0]-1, head[1]]
        elif action == 1: new_head = [head[0]+1, head[1]]
        elif action == 2: new_head = [head[0], head[1]-1]
        elif action == 3: new_head = [head[0], head[1]+1]
        else: return -1.0, True
        if (new_head[0] < 0 or new_head[0] >= self.size or 
            new_head[1] < 0 or new_head[1] >= self.size or 
            new_head in self.snake):
            return -1.0, True
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.spawn_food(); return 1.0, False
        else:
            self.snake.pop(); return 0.0, False

game = SnakeGame()

@app.get("/reset")
async def reset(size: int = 10):
    game.size = size; game.reset()
    await manager.broadcast(json.dumps({"type": "state", "size": game.size, "snake": game.snake, "food": game.food}))
    return {"size": game.size, "snake": game.snake, "food": game.food}

@app.post("/step")
async def step(action: int):
    reward, done = game.step(action)
    await manager.broadcast(json.dumps({"type": "state", "size": game.size, "snake": game.snake, "food": game.food, "reward": reward, "done": done}))
    return {"reward": reward, "done": done, "snake": game.snake, "food": game.food}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"type": "state", "size": game.size, "snake": game.snake, "food": game.food}))
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
