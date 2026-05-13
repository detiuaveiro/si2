import asyncio
import json
import logging
import os
from typing import List, Set, Dict

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

class MazeGame:
    def __init__(self, size=10):
        self.size = size
        self.reset()

    def reset(self):
        # Simple random maze generation
        self.grid = np.zeros((self.size, self.size), dtype=int)
        # Add some obstacles
        for _ in range(int(self.size * self.size * 0.2)):
            self.grid[np.random.randint(0, self.size), np.random.randint(0, self.size)] = 1
        
        self.start = [0, 0]
        self.target = [self.size - 1, self.size - 1]
        self.grid[self.start[0], self.start[1]] = 0
        self.grid[self.target[0], self.target[1]] = 0
        
        self.agent_pos = list(self.start)
        self.done = False
        self.path_taken = [list(self.start)]

    def get_state(self):
        # Return local 3x3 grid around agent + relative target pos
        x, y = self.agent_pos
        local_grid = []
        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                if 0 <= i < self.size and 0 <= j < self.size:
                    local_grid.append(float(self.grid[i, j]))
                else:
                    local_grid.append(1.0) # Wall
        
        rel_target = [float(self.target[0] - x), float(self.target[1] - y)]
        return local_grid + rel_target

    def move(self, action: int):
        if self.done: return
        
        x, y = self.agent_pos
        nx, ny = x, y
        if action == 0: nx -= 1 # Up
        elif action == 1: nx += 1 # Down
        elif action == 2: ny -= 1 # Left
        elif action == 3: ny += 1 # Right
        
        if 0 <= nx < self.size and 0 <= ny < self.size and self.grid[nx, ny] == 0:
            self.agent_pos = [nx, ny]
            self.path_taken.append(list(self.agent_pos))
            if self.agent_pos == self.target:
                self.done = True
        
        return self.get_state()

game = MazeGame()
clients: Set[WebSocket] = set()

async def broadcast_state():
    payload = json.dumps({
        "type": "state",
        "grid": game.grid.tolist(),
        "agent_pos": game.agent_pos,
        "target": game.target,
        "path": game.path_taken,
        "done": game.done
    })
    if clients:
        # Create a list of send tasks
        tasks = [client.send_text(payload) for client in clients]
        await asyncio.gather(*tasks, return_exceptions=True)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        # Send initial state
        await websocket.send_text(json.dumps({
            "type": "state",
            "grid": game.grid.tolist(),
            "agent_pos": game.agent_pos,
            "target": game.target,
            "path": game.path_taken,
            "done": game.done
        }))
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "move":
                action = msg.get("action")
                game.move(action)
                await broadcast_state()
            elif msg.get("type") == "reset":
                game.reset()
                await broadcast_state()
    except WebSocketDisconnect:
        clients.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
