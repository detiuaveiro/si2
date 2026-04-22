import argparse
import os

import uvicorn
from agent import TicTacAgent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = TicTacAgent()


@app.get("/")
async def get_index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


def parse_board_and_turn(board_str):
    """Translates HTML board (0,1,2) to ML board (0,1,-1) and determines whose turn it is."""
    board_list = [1 if c == "1" else (-1 if c == "2" else 0) for c in board_str]
    x_count = board_list.count(1)
    o_count = board_list.count(-1)
    # If counts are equal, it's X's turn (1). Otherwise, O's turn (-1).
    current_player = 1 if x_count == o_count else -1
    return board_list, current_player


@app.get("/move")
def get_move(board: str, temp: float = 1.0):
    board_list, current_player = parse_board_and_turn(board)
    move = agent.choose_move(board_list, current_player)
    return {"move": move}


@app.get("/probs")
def get_probs(board: str):
    board_list, current_player = parse_board_and_turn(board)
    probs = agent.get_probs(board_list, current_player)
    return {"probs": probs.tolist()}


def run_training(args):
    # Delegate all training logic directly to the ML agent's Monte Carlo simulation
    agent.train(games=args.epochs)
    agent.save(args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MSc ML Tic-Tac-Toe")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-e", "--epochs", type=int, default=15000, help="Number of self-play games")
    parser.add_argument("-o", "--output", default="model.joblib")
    parser.add_argument("-i", "--input", default="model.joblib")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.mode == "train":
        run_training(args)
    else:
        agent.load(args.input)
        uvicorn.run(app, host=args.host, port=args.port)
