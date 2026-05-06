import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
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

class TicTacToe:
    def __init__(self): self.reset()
    def reset(self): self.board = [0] * 9; return self.board
    def check_winner(self):
        b = self.board
        for i in range(3):
            if abs(sum(b[i*3:(i+1)*3])) == 3: return b[i*3]
            if abs(sum(b[i::3])) == 3: return b[i]
        if abs(sum(b[0::4])) == 3: return b[0]
        if abs(sum(b[2:7:2])) == 3: return b[2]
        if 0 not in b: return 0
        return None
    def move(self, index: int, player: int):
        if 0 <= index < 9 and self.board[index] == 0:
            self.board[index] = player; return True
        return False

game = TicTacToe()

@app.get("/reset")
async def reset():
    state = game.reset()
    await manager.broadcast(json.dumps({"type": "state", "board": state}))
    return {"board": state}

@app.post("/move")
async def move(index: int, player: int):
    success = game.move(index, player)
    winner = game.check_winner()
    await manager.broadcast(json.dumps({"type": "state", "board": game.board, "winner": winner}))
    return {"success": success, "board": game.board, "winner": winner}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"type": "state", "board": game.board, "winner": game.check_winner()}))
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
