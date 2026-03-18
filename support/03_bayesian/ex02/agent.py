import json
import os

import numpy as np


class TicTacAgent:
    def __init__(self):
        self.knowledge = {}  # {board_key: [probs]}

    def get_board_key(self, board):
        return "".join(map(str, board))

    def get_probs(self, board):
        key = self.get_board_key(board)
        if key not in self.knowledge:
            # Initialize: 1.0 for empty, 0.0 for occupied
            probs = np.array([1.0 if c == 0 else 0.0 for c in board])
            if np.sum(probs) > 0:
                probs /= np.sum(probs)
            self.knowledge[key] = probs.tolist()
        return np.array(self.knowledge[key])

    def select_move(self, board, temp=1.0, deterministic=False):
        probs = self.get_probs(board)
        if np.sum(probs) == 0:
            return None

        if deterministic:
            # Pick the absolute best move based on learned experience
            return int(np.argmax(probs))

        # Otherwise, use Boltzmann sampling for training/variety
        logits = np.log(probs + 1e-10)
        exp_logits = np.exp(logits / temp)
        softmax_probs = exp_logits / np.sum(exp_logits)
        return int(np.random.choice(range(9), p=softmax_probs))

    def update(self, history, result, lr, gamma=0.9):
        # Reverse history to give more credit to the final moves
        for i, (key, action) in enumerate(reversed(history)):
            # Ensure the key exists in knowledge before accessing
            if key not in self.knowledge:
                # Convert string key back to list of ints for get_probs
                board_list = [int(c) for c in key]
                self.get_probs(board_list)
            # The reward fades the further back we go
            discounted_reward = result * (gamma**i)

            probs = np.array(self.knowledge[key])
            board_mask = np.array([1.0 if c == "0" else 0.0 for c in key])

            if discounted_reward > 0:
                probs[action] += lr * discounted_reward
            else:
                probs[action] = max(0.0, probs[action] + (lr * discounted_reward))

            probs *= board_mask
            total = np.sum(probs)
            if total > 0:
                self.knowledge[key] = (probs / total).tolist()

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.knowledge, f)

    def load(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                self.knowledge = json.load(f)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.knowledge = json.load(f)
