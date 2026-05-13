import argparse
import pickle
import random
from typing import Dict, Optional, Tuple, Any

import numpy as np
from tqdm import tqdm

class HotColdEnv:
    """
    Environment for the Hot/Cold number guessing game.
    State is represented as a tuple (curr_low, curr_high).
    """
    def __init__(self, low: int = 1, high: int = 100) -> None:
        self.low_limit: int = low
        self.high_limit: int = high
        self.secret: int = 0
        self.curr_low: int = 0
        self.curr_high: int = 0
        self.done: bool = False
        self.reset()

    def reset(self) -> Tuple[int, int]:
        """Resets the environment to a new secret number and initial range."""
        self.secret = random.randint(self.low_limit, self.high_limit)
        self.curr_low = self.low_limit
        self.curr_high = self.high_limit
        self.done = False
        return (self.curr_low, self.curr_high)

    def step(self, action: int) -> Tuple[Tuple[int, int], float, bool]:
        """
        Executes one step in the environment.
        Returns: (next_state, reward, done)
        """
        guess = action
        
        # Penalize guessing outside the current known range heavily
        if guess < self.curr_low or guess > self.curr_high:
            reward = -10.0
            # Clip guess to remain in logic for range update
            guess = max(self.curr_low, min(self.curr_high, guess))
        else:
            reward = -1.0
        
        if guess == self.secret:
            reward = 100.0
            self.done = True
        elif guess < self.secret:
            self.curr_low = guess + 1
        else:
            self.curr_high = guess - 1
            
        if self.curr_low > self.curr_high:
            self.done = True 
            
        return (self.curr_low, self.curr_high), reward, self.done

class QLearningAgent:
    """
    Q-Learning agent with epsilon-greedy policy.
    Uses a dictionary-based Q-table for state-action values.
    """
    def __init__(
        self, 
        action_size: int = 100, 
        learning_rate: float = 0.1, 
        discount_factor: float = 0.9, 
        epsilon: float = 1.0, 
        epsilon_decay: float = 0.9995
    ) -> None:
        self.q_table: Dict[Tuple[int, int], np.ndarray[Any, np.dtype[np.float64]]] = {}
        self.action_size: int = action_size
        self.lr: float = learning_rate
        self.gamma: float = discount_factor
        self.epsilon: float = epsilon
        self.epsilon_decay: float = epsilon_decay

    def get_q_values(self, state: Tuple[int, int]) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Retrieves Q-values for a given state, initializing if necessary."""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_size, dtype=np.float64)
        return self.q_table[state]

    def choose_action(self, state: Tuple[int, int]) -> int:
        """Selects an action based on epsilon-greedy policy."""
        if random.random() < self.epsilon:
            return random.randint(1, self.action_size)
        return int(np.argmax(self.get_q_values(state)) + 1)

    def learn(
        self, 
        state: Tuple[int, int], 
        action: int, 
        reward: float, 
        next_state: Tuple[int, int], 
        done: bool
    ) -> None:
        """Updates the Q-table using the Q-learning rule."""
        old_value = self.get_q_values(state)[action - 1]
        if done:
            target = reward
        else:
            next_max = np.max(self.get_q_values(next_state))
            target = reward + self.gamma * next_max
        
        new_value = (1 - self.lr) * old_value + self.lr * target
        self.q_table[state][action - 1] = new_value
        
        if done:
            self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)

    def save(self, file_path: str) -> None:
        """Serializes the agent state to a file."""
        with open(file_path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self, file_path: str) -> None:
        """Deserializes the agent state from a file."""
        with open(file_path, 'rb') as f:
            self.q_table = pickle.load(f)

def train(episodes: int, low: int, high: int) -> QLearningAgent:
    """Trains the Q-learning agent in the HotCold environment."""
    env = HotColdEnv(low, high)
    agent = QLearningAgent(action_size=high)
    
    for _ in tqdm(range(episodes), desc="Training"):
        state = env.reset()
        done = False
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.learn(state, action, reward, next_state, done)
            state = next_state
            
    return agent

def play(agent: QLearningAgent, low: int, high: int, secret: Optional[int] = None) -> bool:
    """Executes a play session with a trained agent."""
    env = HotColdEnv(low, high)
    state = env.reset()
    if secret:
        env.secret = secret
    
    print(f"Secret Number: {env.secret}")
    turns = 0
    done = False
    reward = 0.0
    while not done:
        turns += 1
        action = int(np.argmax(agent.get_q_values(state)) + 1)
        print(f"Turn {turns}: Range [{state[0]}, {state[1]}] -> Agent guesses {action}")
        state, reward, done = env.step(action)
        if turns > high: 
            break
        
    if (done and reward == 100.0):
        print(f"Agent won in {turns} turns!")
        return True
    else:
        print("Agent failed.")
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="Q-Learning Agent for Hot/Cold Game")
    
    # Base arguments
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True, help="Mode: train or play")
    parser.add_argument("-l", "--low", type=int, default=1, help="Lowest possible number")
    parser.add_argument("-hi", "--high", type=int, default=100, help="Highest possible number")
    parser.add_argument("-o", "--output", type=str, default="agent.pkl", help="Path to save/load the agent")

    # Training specific group
    train_group = parser.add_argument_group("Training Options")
    train_group.add_argument("-e", "--episodes", type=int, default=200000, help="Number of training episodes")

    # Play specific group
    play_group = parser.add_argument_group("Playing Options")
    play_group.add_argument("-s", "--secret", type=int, default=None, help="Specific secret number for testing")

    args = parser.parse_args()

    if args.mode == "train":
        agent = train(args.episodes, args.low, args.high)
        agent.save(args.output)
        print(f"Agent saved to {args.output}")
    else:
        agent = QLearningAgent(action_size=args.high)
        try:
            agent.load(args.output)
            print(f"Agent loaded from {args.output}")
        except FileNotFoundError:
            print(f"Error: Agent file {args.output} not found. Run training first.")
            return

        play(agent, args.low, args.high, args.secret)

if __name__ == "__main__":
    main()
