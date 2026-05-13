import argparse
import asyncio
import json
import os
from collections import deque

import numpy as np
import websockets
from tqdm import tqdm

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

WS_URL = os.environ.get("WS_URL", "ws://localhost:8765/ws")


class TQDMCallback(keras.callbacks.Callback):
    def on_train_begin(self, logs=None):
        self.pbar = tqdm(total=self.params["epochs"], desc="Training", unit="epoch")

    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs:
            self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})

    def on_train_end(self, logs=None):
        self.pbar.close()


class SnakeSimulator:
    def __init__(self, size=10):
        self.size = size

    def generate_data(self, episodes=100):
        states, actions = [], []
        for _ in tqdm(range(episodes), desc="Simulating Snake"):
            snake = [[self.size // 2, self.size // 2]]
            food = [np.random.randint(0, self.size), np.random.randint(0, self.size)]
            
            for _ in range(200):
                a = self._get_expert_action(snake, food)
                if a is None: break
                
                states.append(self._get_visual_state(snake, food))
                actions.append(a)
                
                head = list(snake[0])
                if a == 0: head[0] -= 1
                elif a == 1: head[1] += 1
                elif a == 2: head[0] += 1
                elif a == 3: head[1] -= 1
                
                if head[0] < 0 or head[0] >= self.size or head[1] < 0 or head[1] >= self.size or head in snake:
                    break
                
                snake.insert(0, head)
                if head == food:
                    food = [np.random.randint(0, self.size), np.random.randint(0, self.size)]
                    while food in snake:
                        food = [np.random.randint(0, self.size), np.random.randint(0, self.size)]
                else:
                    snake.pop()
                    
        return np.array(states), np.array(actions)

    def _get_visual_state(self, snake, food):
        state = np.zeros((self.size, self.size, 3), dtype=np.float32)
        for b in snake[1:]: state[b[0], b[1], 0] = 1.0
        state[snake[0][0], snake[0][1], 1] = 1.0
        state[food[0], food[1], 2] = 1.0
        return state

    def _get_expert_action(self, snake, food):
        q = deque([(tuple(snake[0]), [])])
        v = set(tuple(p) for p in snake)
        while q:
            (x, y), p = q.popleft()
            if [x, y] == food: return p[0]
            for dx, dy, a in [(-1, 0, 0), (0, 1, 1), (1, 0, 2), (0, -1, 3)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) not in v:
                    v.add((nx, ny))
                    q.append(((nx, ny), p + [a]))
        return None


def train(epochs=20, batch_size=32, episodes=100):
    sim = SnakeSimulator()
    X, y = sim.generate_data(episodes=episodes)
    y_oh = keras.utils.to_categorical(y, 4)
    
    model = keras.Sequential([
        keras.layers.Input(shape=(10, 10, 3)),
        keras.layers.Conv2D(16, 3, activation="relu", padding="same"),
        keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
        keras.layers.Flatten(),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(4, activation="softmax")
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    print(f"Training for {epochs} epochs...")
    model.fit(X, y_oh, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0, callbacks=[TQDMCallback()])
    model.save("model.keras")


async def play():
    if not os.path.exists("model.keras"):
        print("Train first.")
        return
    model = keras.models.load_model("model.keras")
    
    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected to backend. Playing Snake...")
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "state":
                    snake = data.get("snake")
                    food = data.get("food")
                    size = data.get("size")
                    
                    state = np.zeros((size, size, 3), dtype=np.float32)
                    for b in snake[1:]: state[b[0], b[1], 0] = 1.0
                    state[snake[0][0], snake[0][1], 1] = 1.0
                    state[food[0], food[1], 2] = 1.0
                    
                    prediction = model.predict(np.array([state]), verbose=0)
                    action = int(np.argmax(prediction[0]))
                    
                    await websocket.send(json.dumps({"type": "action", "action": action}))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snake Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-e", "--epochs", type=int, default=20)
    parser.add_argument("-ep", "--episodes", type=int, default=100)
    args = parser.parse_args()

    if args.mode == "train":
        train(epochs=args.epochs, episodes=args.episodes)
    else:
        try:
            asyncio.run(play())
        except KeyboardInterrupt:
            pass
