import argparse
import asyncio
import json
import os
import random
from collections import deque
from typing import Deque, List, Tuple, Any

import numpy as np
import websockets
from tqdm import tqdm

# Set Keras backend to JAX
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

WS_URL: str = os.environ.get("WS_URL", "ws://localhost:8765/ws")


class BouncingBallEnv:
    """
    Local simulator perfectly aligned with backend physics.
    State: [bx, by, bvx, bvy, px]
    """

    def __init__(self, width: float = 1.0, height: float = 1.0, paddle_width: float = 0.2) -> None:
        self.width = width
        self.height = height
        self.paddle_width = paddle_width
        self.paddle_speed: float = 0.02
        self.g: float = 0.0015
        self.bx: float = 0.5
        self.by: float = 0.1
        self.bvx: float = 0.0
        self.bvy: float = 0.0
        self.px: float = 0.5
        self.reset()

    def reset(self) -> List[float]:
        self.bx = 0.5
        self.by = 0.1
        self.bvx = np.random.uniform(-0.01, 0.01)
        self.bvy = 0.0
        self.px = 0.5
        return self._get_state()

    def _get_state(self) -> List[float]:
        return [float(self.bx), float(self.by), float(self.bvx), float(self.bvy), float(self.px)]

    def step(self, action: int) -> Tuple[List[float], float, bool]:
        """
        Actions: 0: Left, 1: Stay, 2: Right
        """
        if action == 0:
            self.px -= self.paddle_speed
        elif action == 2:
            self.px += self.paddle_speed

        self.px = float(np.clip(self.px, self.paddle_width / 2, self.width - self.paddle_width / 2))

        # Gravity and Velocity
        self.bvy += self.g
        self.bx += self.bvx
        self.by += self.bvy

        # Wall collisions
        if self.bx <= 0 or self.bx >= self.width:
            self.bvx *= -1
            self.bx = float(np.clip(self.bx, 0.0, self.width))

        if self.by <= 0:
            self.bvy *= -1
            self.by = 0.0

        done = False
        # Reward Strategy: Positive for being centered under the ball, negative for missing
        # 1. Continuous reward for tracking
        reward = 1.0 - (abs(self.bx - self.px) / (self.paddle_width / 2))
        reward = max(0.0, reward) # Reward is 0 to 1 when ball is over paddle

        # 2. Episode termination events
        if self.by >= self.height - 0.05:
            if abs(self.bx - self.px) < self.paddle_width / 2:
                reward += 10.0  # Large bonus for successful hit
                self.bvy = -abs(self.bvy)
                self.by = self.height - 0.05
            else:
                reward -= 10.0  # Large penalty for miss
                done = True

        return self._get_state(), float(reward), done


class DQNAgent:
    """
    DQN Agent using standard Keras methods for stability.
    """

    def __init__(
        self,
        state_size: int = 5,
        action_size: int = 3,
        lr: float = 0.001,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.99,
    ) -> None:
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.lr = lr

        self.memory: Deque[Tuple[np.ndarray[Any, Any], int, float, np.ndarray[Any, Any], bool]] = deque(maxlen=20000)

        self.net = self._build_model()
        self.target_net = self._build_model()
        self.update_target_model()

    def _build_model(self) -> keras.Model:
        model = keras.Sequential(
            [
                keras.layers.Input(shape=(self.state_size,)),
                keras.layers.Dense(32, activation="relu"),
                keras.layers.Dense(32, activation="relu"),
                keras.layers.Dense(self.action_size, activation="linear"),
            ]
        )
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=self.lr), loss="mse")
        return model

    def update_target_model(self) -> None:
        self.target_net.set_weights(self.net.get_weights())

    def remember(self, state: List[float], action: int, reward: float, next_state: List[float], done: bool) -> None:
        self.memory.append(
            (np.array(state, dtype=np.float32), action, reward, np.array(next_state, dtype=np.float32), done)
        )

    def get_expert_action(self, state: List[float]) -> int:
        """Heuristic: match paddle center with ball x."""
        bx, _, _, _, px = state
        if bx < px - 0.01:
            return 0
        if bx > px + 0.01:
            return 2
        return 1

    def choose_action(self, state: List[float], explore: bool = True) -> int:
        if explore and random.random() <= self.epsilon:
            # Guided exploration: high chance to use expert while exploring
            if random.random() < 0.7:
                return self.get_expert_action(state)
            return random.randrange(self.action_size)
        
        q_values = self.net.predict(np.array([state], dtype=np.float32), verbose=0)
        return int(np.argmax(q_values[0]))

    def replay(self, batch_size: int) -> float:
        if len(self.memory) < batch_size:
            return 0.0

        minibatch = random.sample(self.memory, batch_size)
        states = np.array([m[0] for m in minibatch])
        actions = np.array([m[1] for m in minibatch])
        rewards = np.array([m[2] for m in minibatch])
        next_states = np.array([m[3] for m in minibatch])
        dones = np.array([m[4] for m in minibatch])

        # Using target network for Bellman update
        targets = self.net.predict(states, verbose=0)
        target_next = self.target_net.predict(next_states, verbose=0)

        for i in range(batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * np.amax(target_next[i])

        history = self.net.fit(states, targets, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return float(history.history['loss'][0])

    def save(self, name: str) -> None:
        self.net.save(name)

    def load(self, name: str) -> None:
        self.net = keras.models.load_model(name)


def train(episodes: int, batch_size: int = 64) -> DQNAgent:
    env = BouncingBallEnv()
    agent = DQNAgent()

    # Pre-fill memory with Expert demonstrations to speed up convergence
    print("Pre-filling memory with Expert demonstrations...")
    for _ in range(20):
        state = env.reset()
        done = False
        while not done:
            action = agent.get_expert_action(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state

    pbar = tqdm(range(episodes), desc="Training DQN")
    for e in pbar:
        state = env.reset()
        total_reward = 0.0
        for _ in range(500):
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            if done:
                break
        
        loss = agent.replay(batch_size)
        if e % 5 == 0:
            agent.update_target_model()
            pbar.set_postfix({"r": f"{total_reward:.1f}", "l": f"{loss:.4f}", "eps": f"{agent.epsilon:.2f}"})

    return agent


async def play(model_path: str) -> None:
    if not os.path.exists(model_path):
        print(f"Error: Model {model_path} not found.")
        return

    agent = DQNAgent()
    agent.load(model_path)
    
    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected to backend. Playing...")
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "state":
                    state = data["state"]
                    state_arr = np.array([state], dtype=np.float32)
                    
                    prediction = agent.net.predict(state_arr, verbose=0)[0]
                    action = int(np.argmax(prediction))
                    
                    await websocket.send(json.dumps({
                        "type": "activations",
                        "layers": [3],
                        "activations": [prediction.tolist()],
                        "chosen_action": action
                    }))

                    await websocket.send(json.dumps({"type": "action", "action": action}))
    except Exception as e:
        print(f"Error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="DQN Agent for Bouncing Ball")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-o", "--output", type=str, default="model.keras")

    t_group = parser.add_argument_group("Training Options")
    t_group.add_argument("-e", "--episodes", type=int, default=100)
    t_group.add_argument("-b", "--batch-size", type=int, default=64)

    args = parser.parse_args()

    if args.mode == "train":
        agent = train(args.episodes, args.batch_size)
        agent.save(args.output)
        print(f"Agent saved to {args.output}")
    elif args.mode == "play":
        asyncio.run(play(args.output))


if __name__ == "__main__":
    main()
