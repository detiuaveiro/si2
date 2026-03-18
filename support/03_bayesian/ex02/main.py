import argparse
import os
import random

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from tqdm import tqdm

from .agent import TicTacAgent

app = FastAPI()

# Allow CORS so the HTML can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = TicTacAgent()


def check_winner(b):
    win_configs = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]
    for c in win_configs:
        if b[c[0]] != 0 and b[c[0]] == b[c[1]] == b[c[2]]:
            return b[c[0]]
    return 0.5 if 0 not in b else 0


# --- ROUTES ---
@app.get("/")
async def get_index():
    # Serves the HTML file
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


@app.get("/move")
def get_move(board: str, temp: float = 1.0):
    board_list = [int(c) for c in board]
    move = agent.select_move(board_list, temp=temp, deterministic=True)
    return {"move": move}


@app.get("/probs")
def get_probs(board: str):
    board_list = [int(c) for c in board]
    probs = agent.get_probs(board_list)
    return {"probs": probs.tolist()}


# --- TRAINING LOGIC ---
def run_training(args):
    trainer = TicTacAgent()

    # Hyperparameter for decay (can be added to argparse)
    # Higher decay means the LR drops faster
    decay_rate = 0.0001

    for epoch in tqdm(range(args.epochs), desc="Training"):
        # CALCULATE DECAYED LEARNING RATE
        # Formula: lr = lr_initial / (1 + decay * epoch)
        current_lr = args.learning_rate / (1.0 + decay_rate * epoch)

        board = [0] * 9
        history = {1: [], 2: []}
        turn = 1

        while True:
            if epoch % 10 == 0:
                # Every 10th game, play against a RANDOM opponent
                # This forces the learner to handle 'unexpected' moves
                move = random.choice([i for i, x in enumerate(board) if x == 0])
            else:
                # Otherwise, play against itself
                move = trainer.select_move(board, temp=args.temp)
            if move is None:
                break

            history[turn].append((trainer.get_board_key(board), move))
            board[move] = turn
            res = check_winner(board)

            if res != 0:
                if res == 0.5:
                    trainer.update(history[1], 0.5, current_lr)
                    trainer.update(history[2], 0.5, current_lr)
                else:
                    winner, loser = (1, 2) if res == 1 else (2, 1)
                    trainer.update(history[winner], 1, current_lr)
                    trainer.update(history[loser], -1, current_lr)
                break
            turn = 2 if turn == 1 else 1

    trainer.save(args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MSc Probabilistic Tic-Tac-Toe")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)

    train_group = parser.add_argument_group("Training Options")
    train_group.add_argument("-e", "--epochs", type=int, default=1000)
    train_group.add_argument("-lr", "--learning-rate", type=float, default=0.2)
    train_group.add_argument("-t", "--temp", type=float, default=1.0)
    train_group.add_argument("-o", "--output", default="model.json")

    play_group = parser.add_argument_group("Play Options")
    play_group.add_argument("-i", "--input", default="model.json")
    play_group.add_argument("--host", default="0.0.0.0")
    play_group.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.mode == "train":
        run_training(args)
    else:
        # Load the model into the global agent used by routes
        agent.load(args.input)
        uvicorn.run(app, host=args.host, port=args.port)
