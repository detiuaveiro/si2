import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from typing import List
import json
from collections import deque

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

class MazeEnv:
    def __init__(self, size=10, prob=0.2):
        self.size = size; self.prob = prob; self.maze = None; self.agent_pos = [0, 0]
    def generate_maze(self):
        m = np.random.choice([0, 1], size=(self.size, self.size), p=[1-self.prob, self.prob])
        m[0,0] = m[self.size-1, self.size-1] = 0
        return m
    def get_shortest_path(self, maze):
        s, g = (0,0), (self.size-1, self.size-1)
        q = deque([(s, [])]); v = {s}
        while q:
            (x, y), p = q.popleft()
            if (x, y) == g: return p
            for dx, dy, a in [(-1,0,0),(1,0,1),(0,-1,2),(0,1,3)]:
                nx, ny = x+dx, y+dy
                if 0<=nx<self.size and 0<=ny<self.size and maze[nx,ny]==0 and (nx,ny) not in v:
                    v.add((nx,ny)); q.append(((nx,ny), p+[a]))
        return None
    def reset(self):
        self.maze = self.generate_maze()
        path = self.get_shortest_path(self.maze)
        while path is None:
            self.maze = self.generate_maze(); path = self.get_shortest_path(self.maze)
        self.agent_pos = [0, 0]
        return self.maze.tolist(), path
    def get_local(self, pos):
        x, y, r = pos[0], pos[1], 1
        g = []
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                nx, ny = x+dx, y+dy
                g.append(int(self.maze[nx,ny]) if 0<=nx<self.size and 0<=ny<self.size else 1)
        return g

env = MazeEnv()

@app.get("/reset")
async def reset():
    maze, path = env.reset()
    state_msg = {"type": "state", "maze": maze, "agent_pos": env.agent_pos, "goal": [env.size-1, env.size-1]}
    await manager.broadcast(json.dumps(state_msg))
    return {"maze": maze, "shortest_path": path}

@app.post("/move")
async def move(pos: List[int]):
    env.agent_pos = pos
    state_msg = {"type": "state", "maze": env.maze.tolist(), "agent_pos": env.agent_pos, "goal": [env.size-1, env.size-1]}
    await manager.broadcast(json.dumps(state_msg))
    return {"status": "ok"}

@app.post("/local")
def get_local(pos: List[int]):
    return {"local": env.get_local(tuple(pos))}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        if env.maze is not None:
            await websocket.send_text(json.dumps({"type": "state", "maze": env.maze.tolist(), "agent_pos": env.agent_pos, "goal": [env.size-1, env.size-1]}))
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
