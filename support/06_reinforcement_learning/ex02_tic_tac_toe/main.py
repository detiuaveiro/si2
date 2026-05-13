import argparse
import asyncio
import json
import os
import pickle
import random
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import websockets
from tqdm import tqdm

WS_URL = os.environ.get("WS_URL", "ws://localhost:8765/ws")


class TicTacToeEnv:
    """
    Environment for the Tic-Tac-Toe game used during training.
    Board is a list of 9 integers: 0 (empty), 1 (X), -1 (O).
    """

    def __init__(self) -> None:
        self.board: List[int] = [0] * 9
        self.current_player: int = 1
        self.done: bool = False
        self.winner: Optional[int] = None

    def reset(self) -> List[int]:
        """Resets the environment for a new game."""
        self.board = [0] * 9
        self.current_player = 1
        self.done = False
        self.winner = None
        return self.board

    def step(self, action: int) -> Tuple[List[int], float, bool]:
        """Executes a move on the board."""
        if self.board[action] != 0 or self.done:
            return self.board, -10.0, True  # Illegal move

        self.board[action] = self.current_player
        self.winner = self.check_winner(self.board)

        if self.winner is not None:
            self.done = True
            if self.winner == 0:
                reward = 0.0  # Draw
            else:
                reward = 1.0  # Current player wins
        else:
            reward = 0.0
            self.current_player *= -1

        return self.board, reward, self.done

    @staticmethod
    def check_winner(b: List[int]) -> Optional[int]:
        """Checks if there is a winner on the board."""
        for i in range(3):
            if abs(sum(b[i * 3 : (i + 1) * 3])) == 3:
                return b[i * 3]
            if abs(sum(b[i::3])) == 3:
                return b[i]
        if abs(sum(b[0::4])) == 3:
            return b[0]
        if abs(sum(b[2:7:2])) == 3:
            return b[2]
        if 0 not in b:
            return 0
        return None


class MinimaxAgent:
    """Agent that plays optimally using minimax algorithm with caching."""

    def __init__(self, player: int) -> None:
        self.player = player
        self._memo: Dict[Tuple[Tuple[int, ...], int], Tuple[int, Optional[int]]] = {}

    def choose_action(self, board: List[int]) -> int:
        """Returns the optimal move for the given board."""
        _, move = self._minimax(tuple(board), self.player)
        return move if move is not None else -1

    def _minimax(self, board: Tuple[int, ...], player: int) -> Tuple[int, Optional[int]]:
        state_key = (board, player)
        if state_key in self._memo:
            return self._memo[state_key]

        winner = TicTacToeEnv.check_winner(list(board))
        if winner is not None:
            if winner == 0:
                return 0, None
            return (1 if winner == player else -1), None

        best_score = -2
        best_move = None

        b_list = list(board)
        for i in range(9):
            if b_list[i] == 0:
                b_list[i] = player
                score, _ = self._minimax(tuple(b_list), -player)
                score *= -1
                b_list[i] = 0

                if score > best_score:
                    best_score = score
                    best_move = i

        self._memo[state_key] = (best_score, best_move)
        return best_score, best_move


class QLearningAgent:
    """Classical RL agent using Q-Learning."""

    def __init__(
        self,
        learning_rate: float = 0.2,
        discount_factor: float = 0.95,
        epsilon: float = 0.5,
        epsilon_decay: float = 0.999995,
    ) -> None:
        self.q_table: Dict[str, np.ndarray[Any, np.dtype[np.float64]]] = {}
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

    def _get_state_key(self, board: List[int], player: int) -> str:
        """Normalizes the board from the current player's perspective."""
        # Using string is safe and easy for keys
        normalized = tuple(x * player for x in board)
        return str(normalized)

    def _get_q_values(self, key: str) -> np.ndarray[Any, np.dtype[np.float64]]:
        if key not in self.q_table:
            # Small random init helps breaking ties early
            self.q_table[key] = np.zeros(9, dtype=np.float64)
        return self.q_table[key]

    def choose_action(self, board: List[int], player: int, explore: bool = True) -> int:
        """Chooses an action based on epsilon-greedy policy."""
        key = self._get_state_key(board, player)
        q_values = self._get_q_values(key)

        empty_cells = [i for i, val in enumerate(board) if val == 0]
        if not empty_cells:
            return -1

        if explore and random.random() < self.epsilon:
            return random.choice(empty_cells)

        # Mask illegal moves with -infinity to ensure they are never picked
        masked_q = q_values.copy()
        for i in range(9):
            if board[i] != 0:
                masked_q[i] = -np.inf

        return int(np.argmax(masked_q))

    def learn(
        self,
        state: List[int],
        player: int,
        action: int,
        reward: float,
        next_state: List[int],
        done: bool,
    ) -> None:
        """Updates the Q-table using the standard Q-Learning formula."""
        key = self._get_state_key(state, player)
        q_vals = self._get_q_values(key)
        old_value = q_vals[action]

        if done:
            target = reward
        else:
            # For turn-based games, next_state is after opponent's move
            # From OUR perspective
            next_key = self._get_state_key(next_state, player)
            target = reward + self.gamma * np.max(self._get_q_values(next_key))

        self.q_table[key][action] = old_value + self.lr * (target - old_value)

        if done:
            self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)

    def save(self, file_path: str) -> None:
        """Saves the Q-table to a file."""
        with open(file_path, "wb") as f:
            pickle.dump(self.q_table, f)

    def load(self, file_path: str) -> None:
        """Loads the Q-table from a file."""
        with open(file_path, "rb") as f:
            self.q_table = pickle.load(f)


def train(episodes: int, opponent_type: str = "minimax") -> QLearningAgent:
    """Trains the agent playing against Minimax or Random."""
    env = TicTacToeEnv()
    agent = QLearningAgent()
    minimax = MinimaxAgent(player=-1)

    for _ in tqdm(range(episodes), desc="Training"):
        state = env.reset()
        current_player = 1
        done = False

        # Memory for the last state/action to perform updates
        history: Dict[int, Any] = {
            1: {"s": None, "a": None},
            -1: {"s": None, "a": None}
        }

        # Deterministic vs Random opponent
        is_random_opp = random.random() < 0.2 if opponent_type == "minimax" else True

        while not done:
            if current_player == 1:
                action = agent.choose_action(state, 1)
                
                # If this isn't the first move, we can update the previous state's Q-value
                # because we now know the 'next_state' (the board after opponent's turn)
                if history[1]["s"] is not None:
                    agent.learn(history[1]["s"], 1, history[1]["a"], 0.0, state, False)
                
                history[1]["s"] = list(state)
                history[1]["a"] = action
                
                _, reward, done = env.step(action)
                if done:
                    # Current player (1) won or draw
                    agent.learn(history[1]["s"], 1, action, reward, state, True)
                    # Opponent (-1) lost
                    if history[-1]["s"] is not None:
                        agent.learn(history[-1]["s"], -1, history[-1]["a"], -reward, state, True)
            else:
                # Opponent's turn
                if is_random_opp:
                    empty = [i for i, x in enumerate(state) if x == 0]
                    action = random.choice(empty)
                else:
                    action = minimax.choose_action(state)

                # We can also let the agent learn as the second player!
                # This makes it robust to playing as O.
                if history[-1]["s"] is not None:
                    agent.learn(history[-1]["s"], -1, history[-1]["a"], 0.0, state, False)
                
                history[-1]["s"] = list(state)
                history[-1]["a"] = action

                _, reward, done = env.step(action)
                if done:
                    # Opponent (-1) won or draw
                    agent.learn(history[-1]["s"], -1, action, reward, state, True)
                    # Agent (1) lost
                    if history[1]["s"] is not None:
                        agent.learn(history[1]["s"], 1, history[1]["a"], -reward, state, True)

            current_player *= -1

    return agent


async def play(agent_path: str, agent_player: int = -1) -> None:
    """Connects to the websocket backend."""
    agent = QLearningAgent()
    try:
        agent.load(agent_path)
        print(f"Agent loaded from {agent_path}")
    except FileNotFoundError:
        print("No agent found. Training...")
        agent = train(50000)

    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"Connected to backend. Playing as {'X' if agent_player == 1 else 'O'}...")
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "state":
                    board = data.get("board")
                    winner = data.get("winner")

                    if winner is not None:
                        print(f"Game Over! Winner: {winner}")
                        continue

                    # Turn detection
                    x_count = board.count(1)
                    o_count = board.count(-1)
                    my_turn = (agent_player == 1 and x_count == o_count) or (
                        agent_player == -1 and x_count > o_count
                    )

                    if my_turn:
                        move = agent.choose_action(board, agent_player, explore=False)
                        key = agent._get_state_key(board, agent_player)
                        q_vals = agent._get_q_values(key).tolist()
                        
                        # 1. Send activations for the frontend (proxied by backend)
                        # We include the 'move' so the frontend can highlight it
                        await websocket.send(
                            json.dumps(
                                {
                                    "type": "activations",
                                    "q_vals": q_vals,
                                    "move": move,
                                    "player": agent_player
                                }
                            )
                        )
                        
                        # 2. Send the actual move to the backend to progress the game
                        await websocket.send(
                            json.dumps(
                                {
                                    "type": "move",
                                    "index": move,
                                    "player": agent_player
                                }
                            )
                        )

    except Exception as e:
        print(f"Error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Q-Learning Tic-Tac-Toe")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-o", "--output", type=str, default="tictactoe_qtable.pkl")

    t_group = parser.add_argument_group("Training Options")
    t_group.add_argument("-e", "--episodes", type=int, default=100000)
    t_group.add_argument("-opp_train", "--opponent-train", choices=["random", "minimax"], default="minimax")

    p_group = parser.add_argument_group("Playing Options")
    p_group.add_argument("-p", "--player", type=int, choices=[1, -1], default=-1)

    args = parser.parse_args()

    if args.mode == "train":
        agent = train(args.episodes, args.opponent_train)
        agent.save(args.output)
    elif args.mode == "play":
        asyncio.run(play(args.output, args.player))


if __name__ == "__main__":
    main()
