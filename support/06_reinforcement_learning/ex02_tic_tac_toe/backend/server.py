import uvicorn
import json
import logging
from typing import List, Set
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

class TicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [0] * 9
        self.winner = None
        return self.board

    def check_winner(self):
        b = self.board
        win_configs = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8), # Cols
            (0, 4, 8), (2, 4, 6)             # Diagonals
        ]
        for a, b_idx, c in win_configs:
            if b[a] != 0 and b[a] == b[b_idx] == b[c]:
                self.winner = b[a]
                return b[a]
        if 0 not in b:
            self.winner = 0 # Draw
            return 0
        return None

    def move(self, index: int, player: int):
        if self.winner is not None:
            return False
        if 0 <= index < 9 and self.board[index] == 0:
            self.board[index] = player
            self.check_winner()
            return True
        return False

game = TicTacToe()
clients: Set[WebSocket] = set()

async def broadcast_state():
    payload = json.dumps({
        "type": "state",
        "board": game.board,
        "winner": game.winner
    })
    if clients:
        import asyncio
        await asyncio.gather(*[client.send_text(payload) for client in clients])

@app.get("/reset")
async def reset():
    game.reset()
    await broadcast_state()
    return {"board": game.board}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        # Send initial state
        await websocket.send_text(json.dumps({
            "type": "state",
            "board": game.board,
            "winner": game.winner
        }))
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "move":
                idx = msg.get("index")
                player = msg.get("player")
                if game.move(idx, player):
                    await broadcast_state()
            
            elif msg.get("type") == "reset":
                game.reset()
                await broadcast_state()
            
            elif msg.get("type") == "activations":
                # Proxy activations to other clients (frontend)
                if clients:
                    import asyncio
                    payload = json.dumps(msg)
                    await asyncio.gather(*[client.send_text(payload) for client in clients if client != websocket])

    except WebSocketDisconnect:
        clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
