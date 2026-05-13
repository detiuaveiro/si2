import asyncio
import json
import logging
from typing import Set

import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BallGame:
    def __init__(self):
        self.width = 1.0
        self.height = 1.0
        self.paddle_width = 0.2
        self.g = 0.0015  # Gravity constant
        self.reset()

    def reset(self):
        self.ball_x = 0.5
        self.ball_y = 0.1
        # Constant energy based on max potential at top (y=0)
        self.total_energy = self.g * 1.0 
        self.ball_vx = np.random.uniform(-0.01, 0.01)
        self.ball_vy = 0.0
        self.paddle_x = 0.5
        self.score = 0
        self.done = False
        return self.get_state()

    def get_state(self):
        return [
            float(self.ball_x),
            float(self.ball_y),
            float(self.ball_vx),
            float(self.ball_vy),
            float(self.paddle_x),
        ]

    def update(self, action: int = 1):
        if self.done:
            return self.get_state(), 0.0, True

        # Action: 0: Left, 1: Stay, 2: Right
        paddle_speed = 0.02
        if action == 0:
            self.paddle_x -= paddle_speed
        elif action == 2:
            self.paddle_x += paddle_speed

        self.paddle_x = float(np.clip(self.paddle_x, self.paddle_width / 2, self.width - self.paddle_width / 2))

        # Update physics with energy conservation
        # v_y increases due to gravity
        self.ball_vy += self.g
        
        # Apply velocities
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        # Wall collisions (Elastic)
        if self.ball_x <= 0 or self.ball_x >= self.width:
            self.ball_vx *= -1
            self.ball_x = float(np.clip(self.ball_x, 0, self.width))

        if self.ball_y <= 0:
            self.ball_vy *= -1
            self.ball_y = 0.0

        # Paddle collision
        reward = 0.0
        if self.ball_y >= self.height - 0.05:
            if abs(self.ball_x - self.paddle_x) < self.paddle_width / 2:
                # Elastic Bounce
                self.ball_vy = -abs(self.ball_vy) 
                self.ball_y = self.height - 0.05
                # To prevent energy drift, we could re-normalize, 
                # but simple reversal + gravity is stable enough.
                reward = 1.0
                self.score += 1
            else:
                # Game over
                self.done = True
                reward = -1.0

        return self.get_state(), reward, self.done


game = BallGame()
clients: Set[WebSocket] = set()
current_action = 1  # Default to 'Stay'


async def game_loop():
    global current_action
    while True:
        # Wait for at least one client (agent or frontend) to start the simulation
        if clients and not game.done:
            state, reward, done = game.update(current_action)
            payload = json.dumps(
                {"type": "state", "state": state, "reward": reward, "done": done, "score": game.score}
            )
            # Broadcast to all clients
            await asyncio.gather(*[client.send_text(payload) for client in clients], return_exceptions=True)
        elif game.done:
            # Auto-reset after a short delay
            await asyncio.sleep(2)
            game.reset()
            current_action = 1

        await asyncio.sleep(0.05)  # 20 FPS


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(game_loop())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global current_action
    await websocket.accept()
    clients.add(websocket)
    try:
        # Send initial state
        await websocket.send_text(json.dumps(
            {"type": "state", "state": game.get_state(), "reward": 0, "done": game.done, "score": game.score}
        ))
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "action":
                    current_action = int(msg.get("action", 1))
                elif msg.get("type") == "reset":
                    game.reset()
                    current_action = 1
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
