import argparse
import asyncio
import base64
import hashlib
import json
import os
import socket
import struct

import numpy as np
from tqdm import tqdm

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

WS_HOST = os.environ.get("WS_HOST", "localhost")
WS_PORT = int(os.environ.get("WS_PORT", 8765))


class SimpleWebSocketClient:
    """A minimal WebSocket client implementation using only asyncio and socket."""
    def __init__(self, host, port, path="/ws"):
        self.host = host
        self.port = port
        self.path = path
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        
        # Handshake
        key = base64.b64encode(os.urandom(16)).decode()
        handshake = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        self.writer.write(handshake.encode())
        await self.writer.drain()
        
        response = await self.reader.readuntil(b"\r\n\r\n")
        if b"101 Switching Protocols" not in response:
            raise Exception("WebSocket handshake failed")

    async def send(self, data):
        payload = json.dumps(data).encode()
        header = bytearray([0x81])  # Text frame, final fragment
        length = len(payload)
        
        if length <= 125:
            header.append(0x80 | length)
        elif length <= 65535:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
            
        mask = os.urandom(4)
        header.extend(mask)
        masked_payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        
        self.writer.write(header + masked_payload)
        await self.writer.drain()

    async def receive(self):
        # Read header
        header = await self.reader.readexactly(2)
        second_byte = header[1]
        length = second_byte & 0x7F
        
        if length == 126:
            data = await self.reader.readexactly(2)
            length = struct.unpack("!H", data)[0]
        elif length == 127:
            data = await self.reader.readexactly(8)
            length = struct.unpack("!Q", data)[0]
            
        payload = await self.reader.readexactly(length)
        return json.loads(payload.decode())

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()


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
    print(f"Connecting to ws://{WS_HOST}:{WS_PORT}/ws...")

    client = SimpleWebSocketClient(WS_HOST, WS_PORT)
    try:
        await client.connect()
        print("Connected to backend. Playing...")
        while True:
            data = await client.receive()
            if data.get("type") == "state":
                state = np.array(data["state"]).reshape(1, -1)
                prediction = model.predict(state, verbose=0)
                action = int(np.argmax(prediction[0]))
                
                await client.send({
                    "type": "action",
                    "action": action
                })
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the backend is running.")
    finally:
        await client.close()


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
