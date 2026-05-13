import argparse
import asyncio
import json
import os
import sys

import numpy as np
import websockets
from tqdm import tqdm

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

WS_URL = os.environ.get("WS_URL", "ws://localhost:8765/ws")


class SyntheticDataGenerator:
    def __init__(self, width=1.0, height=1.0, paddle_width=0.2):
        self.width = width
        self.height = height
        self.paddle_width = paddle_width

    def generate(self, num_samples=10000):
        states = []
        actions = []

        for _ in tqdm(range(num_samples), desc="Generating Synthetic Data"):
            # Randomize state
            bx = np.random.uniform(0, self.width)
            by = np.random.uniform(0, self.height)
            bvx = np.random.uniform(-0.02, 0.02)
            bvy = np.random.uniform(-0.02, 0.02)
            px = np.random.uniform(self.paddle_width / 2, self.width - self.paddle_width / 2)

            state = [bx, by, bvx, bvy, px]
            
            # Heuristic action: try to follow the ball
            if bx < px - 0.02:
                action = 0
            elif bx > px + 0.02:
                action = 2
            else:
                action = 1

            states.append(state)
            actions.append(action)

        return np.array(states), np.array(actions)


class TQDMCallback(keras.callbacks.Callback):
    def on_train_begin(self, logs=None):
        self.pbar = tqdm(total=self.params["epochs"], desc="Training", unit="epoch")

    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs:
            self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})

    def on_train_end(self, logs=None):
        self.pbar.close()


def train(epochs=10, batch_size=32, samples=10000):
    generator = SyntheticDataGenerator()
    X, y = generator.generate(num_samples=samples)
    y_oh = keras.utils.to_categorical(y, 3)

    model = keras.Sequential(
        [
            keras.layers.Input(shape=(5,)),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(3, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    
    print(f"Training for {epochs} epochs with batch size {batch_size}...")
    model.fit(
        X, y_oh, 
        epochs=epochs, 
        batch_size=batch_size, 
        validation_split=0.2, 
        verbose=0, 
        callbacks=[TQDMCallback()]
    )
    
    model.save("model.keras")
    print("Model saved to model.keras")


async def play():
    model_path = "model.keras"
    if not os.path.exists(model_path):
        print("Train the model first using --mode train")
        return

    model = keras.models.load_model(model_path)
    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected to backend. Playing...")
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "state":
                    state = np.array(data["state"]).reshape(1, -1)
                    prediction = model.predict(state, verbose=0)
                    action = int(np.argmax(prediction[0]))
                    
                    await websocket.send(json.dumps({
                        "type": "action",
                        "action": action
                    }))
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the backend is running.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bouncing Ball Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True, help="Mode: train or play")
    
    # Training arguments
    parser.add_argument("-e", "--epochs", type=int, default=20, help="Number of epochs for training")
    parser.add_argument("-b", "--batch-size", type=int, default=64, help="Batch size for training")
    parser.add_argument("-s", "--samples", type=int, default=20000, help="Number of synthetic samples to generate")
    
    args = parser.parse_args()

    if args.mode == "train":
        train(epochs=args.epochs, batch_size=args.batch_size, samples=args.samples)
    elif args.mode == "play":
        try:
            asyncio.run(play())
        except KeyboardInterrupt:
            print("\nStopped by user")
