import random

import joblib
import numpy as np
from sklearn.neural_network import MLPRegressor


class TicTacAgent:
    def __init__(self):
        self.model = MLPRegressor(hidden_layer_sizes=(64, 64), max_iter=1000, learning_rate_init=0.01, random_state=42)
        self.is_trained = False

    def check_winner(self, board):
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
        for a, b, c in win_configs:
            if board[a] != 0 and board[a] == board[b] == board[c]:
                return board[a]
        if 0 not in board:
            return 0.5
        return 0

    def _generate_self_play_data(self, games=10000):
        X_data, y_data = [], []
        for _ in range(games):
            board = [0] * 9
            history = []
            turn = 1
            while True:
                valid_moves = [i for i, v in enumerate(board) if v == 0]
                move = random.choice(valid_moves)
                board[move] = turn
                history.append(list(board))

                res = self.check_winner(board)
                if res != 0:
                    final_reward = 0 if res == 0.5 else res
                    for state in history:
                        X_data.append(state)
                        y_data.append(final_reward)
                    break
                turn *= -1
        return np.array(X_data), np.array(y_data)

    def train(self, games=10000):
        print(f"Simulating {games} self-play games for training data...")
        X_train, y_train = self._generate_self_play_data(games)
        print(f"Training Neural Network on {len(X_train)} board states...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        print("Training complete!")

    def choose_move(self, board, player_symbol):
        if not self.is_trained:
            valid = [i for i, v in enumerate(board) if v == 0]
            return random.choice(valid) if valid else None

        best_move, best_val = None, -float("inf") if player_symbol == 1 else float("inf")
        for i in range(9):
            if board[i] == 0:
                next_board = list(board)
                next_board[i] = player_symbol
                val = self.model.predict([next_board])[0]

                if player_symbol == 1 and val > best_val:
                    best_val, best_move = val, i
                elif player_symbol == -1 and val < best_val:
                    best_val, best_move = val, i
        return best_move

    def get_probs(self, board, player_symbol):
        """Evaluates all valid moves to populate the HTML chart."""
        probs = np.zeros(9)
        if not self.is_trained:
            return probs

        valid_moves = [i for i, v in enumerate(board) if v == 0]
        if not valid_moves:
            return probs

        scores = []
        for i in valid_moves:
            next_board = list(board)
            next_board[i] = player_symbol
            val = self.model.predict([next_board])[0]
            # Normalize so "good" moves for the current player map to positive values
            scores.append(val if player_symbol == 1 else -val)

        scores = np.array(scores)
        min_s, max_s = np.min(scores), np.max(scores)

        # Scale scores between 0 and 1 for the bar chart
        norm_scores = (scores - min_s) / (max_s - min_s) if max_s > min_s else np.ones(len(scores)) / len(scores)

        for idx, move in enumerate(valid_moves):
            probs[move] = norm_scores[idx]
        return probs

    def save(self, filename):
        joblib.dump(self.model, filename)
        print(f"Model saved to {filename}")

    def load(self, filename):
        self.model = joblib.load(filename)
        self.is_trained = True
        print(f"Model loaded from {filename}")
