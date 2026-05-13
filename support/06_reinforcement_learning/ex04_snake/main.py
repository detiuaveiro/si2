import argparse
import asyncio
import json
import os
from typing import List, Tuple, Any

import numpy as np
import websockets
from tqdm import tqdm

# Set Keras backend to JAX
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

# Specialized optimization libraries
from pyBlindOpt.de import differential_evolution
from pyBlindOpt.init import quasi_opposition_based

WS_URL: str = os.environ.get("WS_URL", "ws://localhost:8765/ws")


class SnakeSimulator:
    """
    Fast local Snake simulator.
    State: Concise perception vector instead of full pixels.
    """

    def __init__(self, size: int = 10) -> None:
        self.size = size
        self.reset()

    def reset(self) -> np.ndarray:
        self.snake = [[self.size // 2, self.size // 2]]
        self.food = self._generate_food()
        self.score = 0
        self.steps = 0
        self.done = False
        return self._get_perception_state()

    def _generate_food(self) -> List[int]:
        while True:
            food = [np.random.randint(0, self.size), np.random.randint(0, self.size)]
            if food not in self.snake:
                return food

    def _get_perception_state(self) -> np.ndarray:
        """
        Concise 7-element state:
        [food_up, food_right, food_down, food_left, danger_up, danger_right, danger_down, danger_left]
        Actually let's use 8 elements for clarity.
        """
        head = self.snake[0]
        
        # 1. Food relative direction
        f_up = 1.0 if self.food[0] < head[0] else 0.0
        f_down = 1.0 if self.food[0] > head[0] else 0.0
        f_left = 1.0 if self.food[1] < head[1] else 0.0
        f_right = 1.0 if self.food[1] > head[1] else 0.0
        
        # 2. Immediate danger (walls or body)
        def is_unsafe(r, c):
            return r < 0 or r >= self.size or c < 0 or c >= self.size or [r, c] in self.snake

        d_up = 1.0 if is_unsafe(head[0] - 1, head[1]) else 0.0
        d_down = 1.0 if is_unsafe(head[0] + 1, head[1]) else 0.0
        d_left = 1.0 if is_unsafe(head[0], head[1] - 1) else 0.0
        d_right = 1.0 if is_unsafe(head[0], head[1] + 1) else 0.0
        
        return np.array([f_up, f_down, f_left, f_right, d_up, d_down, d_left, d_right], dtype=np.float32)

    def step(self, action: int) -> Tuple[np.ndarray, float, bool]:
        self.steps += 1
        head = list(self.snake[0])
        if action == 0: head[0] -= 1
        elif action == 1: head[1] += 1
        elif action == 2: head[0] += 1
        elif action == 3: head[1] -= 1

        if (head[0] < 0 or head[0] >= self.size or 
            head[1] < 0 or head[1] >= self.size or 
            head in self.snake):
            self.done = True
            return self._get_perception_state(), -10.0, True

        self.snake.insert(0, head)
        reward = 0.1 

        if head == self.food:
            self.score += 1
            reward = 50.0 # High reward for food
            self.food = self._generate_food()
            self.steps = 0 # Reset step counter to allow long snakes
        else:
            self.snake.pop()

        if self.steps > 200: # Timeout for wandering
            self.done = True

        return self._get_perception_state(), reward, self.done


class MLPNeuroAgent:
    """Compact MLP agent (Low dimensionality for fast DE)."""
    def __init__(self) -> None:
        self.model = keras.Sequential([
            keras.layers.Input(shape=(8,)),
            keras.layers.Dense(8, activation="relu"),
            keras.layers.Dense(4, activation="softmax"),
        ])
        self.num_params = sum(np.prod(w.shape) for w in self.model.get_weights())
        self.weight_shapes = [w.shape for w in self.model.get_weights()]

    def set_weights(self, flat_weights: np.ndarray) -> None:
        new_weights = []
        curr = 0
        for shape in self.weight_shapes:
            size = int(np.prod(shape))
            new_weights.append(flat_weights[curr:curr+size].reshape(shape))
            curr += size
        self.model.set_weights(new_weights)

    def get_action(self, state: np.ndarray) -> int:
        prediction = self.model(np.array([state]), training=False)
        return int(np.argmax(np.array(prediction[0])))


def objective_function(flat_weights: np.ndarray, agent: MLPNeuroAgent, episodes: int = 5) -> float:
    agent.set_weights(flat_weights)
    env = SnakeSimulator()
    total_reward = 0.0
    for _ in range(episodes):
        state = env.reset()
        done = False
        while not done:
            action = agent.get_action(state)
            state, reward, done = env.step(action)
            total_reward += reward
    return 1000.0 - (total_reward / episodes)


def train(generations: int, pop_size: int) -> np.ndarray:
    agent = MLPNeuroAgent()
    dim = agent.num_params
    bounds = np.tile([-1.0, 1.0], (dim, 1))
    
    print(f"Starting Neuroevolution (MLP) with {dim} parameters...")
    
    def obj_with_agent(x: np.ndarray) -> float:
        return objective_function(x, agent)
    
    initial_pop = quasi_opposition_based(objective=obj_with_agent, bounds=bounds, n_pop=pop_size, seed=42)

    best_weights, best_score = differential_evolution(
        objective=obj_with_agent,
        bounds=bounds,
        population=initial_pop,
        n_pop=pop_size,
        n_iter=generations,
        variant="best/1/bin",
        F=0.5,
        cr=0.7,
        verbose=True
    )
    
    print(f"Evolution complete. Best reward: {1000.0 - float(best_score):.2f}")
    return best_weights


async def play(model_path: str) -> None:
    if not os.path.exists(model_path):
        print("Model not found.")
        return
    model = keras.models.load_model(model_path)
    # Build dummy agent to get shapes
    agent = MLPNeuroAgent()
    
    print(f"Connecting to {WS_URL}...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected. Playing Snake with MLP Neuroevolution...")
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "state":
                    # Adapt backend state to our perception state
                    sim = SnakeSimulator(size=data["size"])
                    sim.snake = data["snake"]
                    sim.food = data["food"]
                    state = sim._get_perception_state()
                    
                    prediction = model(np.array([state]), training=False)
                    prediction_np = np.array(prediction[0])
                    action = int(np.argmax(prediction_np))
                    
                    await websocket.send(json.dumps({
                        "type": "activations",
                        "layers": [8, 8, 4],
                        "activations": [state.tolist(), prediction_np.tolist()],
                        "chosen_action": action
                    }))
                    await websocket.send(json.dumps({"type": "action", "action": action}))
    except Exception as e:
        print(f"Error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Snake Neuroevolution (MLP)")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-o", "--output", type=str, default="model.keras")
    t_group = parser.add_argument_group("Training Options")
    t_group.add_argument("-g", "--generations", type=int, default=100)
    t_group.add_argument("-p", "--pop-size", type=int, default=50)
    args = parser.parse_args()

    if args.mode == "train":
        best_flat_weights = train(args.generations, args.pop_size)
        final_agent = MLPNeuroAgent()
        final_agent.set_weights(best_flat_weights)
        final_agent.model.save(args.output)
    else:
        asyncio.run(play(args.output))

if __name__ == "__main__":
    main()
