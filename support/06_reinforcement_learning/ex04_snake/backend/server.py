import asyncio
import json
import logging
import random
from typing import List, Set

import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SnakeGame:
    def __init__(self, size=10):
        self.size = size
        self.reset()

    def reset(self):
        self.snake = [[self.size // 2, self.size // 2]]
        self.direction = 1 # Right
        self.food = self._spawn_food()
        self.score = 0
        self.done = False
        return self.get_state()

    def _spawn_food(self):
        while True:
            food = [random.randint(0, self.size - 1), random.randint(0, self.size - 1)]
            if food not in self.snake:
                return food

    def get_state(self):
        return {
            "snake": self.snake,
            "food": self.food,
            "size": self.size,
            "score": self.score,
            "done": self.done
        }

    def update(self, action: int):
        if self.done: return self.get_state()
        
        # 0: Up, 1: Right, 2: Down, 3: Left
        head = list(self.snake[0])
        if action == 0: head[0] -= 1
        elif action == 1: head[1] += 1
        elif action == 2: head[0] += 1
        elif action == 3: head[1] -= 1
        
        # Check collisions
        if (head[0] < 0 or head[0] >= self.size or 
            head[1] < 0 or head[1] >= self.size or 
            head in self.snake):
            self.done = True
            return self.get_state()
            
        self.snake.insert(0, head)
        if head == self.food:
            self.score += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()
            
        return self.get_state()

game = SnakeGame()
clients: Set[WebSocket] = set()
current_action = 1 # Default to Right

async def game_loop():
    global current_action
    while True:
        # Wait for at least one client to start the simulation
        if clients and not game.done:
            game.update(current_action)
            payload = json.dumps({
                "type": "state",
                **game.get_state()
            })
            await asyncio.gather(*[client.send_text(payload) for client in clients], return_exceptions=True)
        elif game.done:
            await asyncio.sleep(2)
            game.reset()
            current_action = 1
            
        await asyncio.sleep(0.2) # 5 FPS for Snake

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(game_loop())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global current_action
    await websocket.accept()
    clients.add(websocket)
    try:
        # Initial state
        await websocket.send_text(json.dumps({
            "type": "state",
            **game.get_state()
        }))
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "action":
                current_action = int(msg.get("action"))
            elif msg.get("type") == "reset":
                game.reset()
                current_action = 1
    except WebSocketDisconnect:
        clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
