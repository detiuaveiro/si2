import argparse
import asyncio
import json
import os

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


def check_winner_local(b):
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


_memo = {}


def minimax(b, p):
    sk = (tuple(b), p)
    if sk in _memo:
        return _memo[sk]
    w = check_winner_local(b)
    if w is not None:
        return w * p, None
    bs, bm = -2, None
    for i in range(9):
        if b[i] == 0:
            b[i] = p
            s, _ = minimax(b, -p)
            s = -s
            b[i] = 0
            if s > bs:
                bs, bm = s, i
    _memo[sk] = (bs, bm)
    return bs, bm


def gen(num=5000):
    states, actions = [], []
    print(f"Generating Tic-Tac-Toe data ({num} samples)...")
    for _ in tqdm(range(num), desc="Simulating"):
        board = [0] * 9
        player = 1
        for _ in range(np.random.randint(0, 7)):
            empty = [i for i, x in enumerate(board) if x == 0]
            if not empty:
                break
            board[np.random.choice(empty)] = player
            player *= -1
            if check_winner_local(board) is not None:
                board, player = [0] * 9, 1
                break
        _, move = minimax(board, player)
        if move is not None:
            states.append([x * player for x in board])
            actions.append(move)
    return np.array(states), np.array(actions)


def train(epochs=20, batch_size=64, samples=5000):
    X, y = gen(num=samples)
    y_oh = keras.utils.to_categorical(y, 9)
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(9,)),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(9, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    print(f"Training for {epochs} epochs...")
    model.fit(
        X,
        y_oh,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.2,
        verbose=0,
        callbacks=[TQDMCallback()],
    )
    model.save("model.keras")


async def play():
    model_path = "model.keras"
    if not os.path.exists(model_path):
        print("Train first.")
        return
    model = keras.models.load_model(model_path)
    # Build model by calling it on dummy data to ensure inputs/outputs are defined
    model(np.zeros((1, 9)))

    # Extract activations from all layers including input
    # We use model.layers to get outputs. 
    # Note: Keras 3 Sequential.layers[0] is the first Dense, so we add input manually in the loop
    activation_layers = [layer.output for layer in model.layers]
    activation_model = keras.Model(inputs=model.inputs, outputs=activation_layers)


    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("Connected to backend. Playing as Player 2 (O)...")
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "state":
                    board = data.get("board")
                    winner = data.get("winner")

                    if winner is not None:
                        print(f"Game Over! Winner: {winner}")
                        continue

                    x_count = board.count(1)
                    o_count = board.count(-1)

                    if x_count > o_count:
                        input_board = np.array([x * -1 for x in board]).reshape(1, -1)
                        activations = activation_model.predict(input_board, verbose=0)
                        act_list = [input_board.tolist()[0]]
                        for act in activations:
                            act_list.append(act.tolist()[0])

                        prediction = activations[-1]
                        probs = prediction[0]
                        for i in range(9):
                            if board[i] != 0:
                                probs[i] = -1

                        move = int(np.argmax(probs))

                        await websocket.send(
                            json.dumps(
                                {
                                    "type": "activations",
                                    "layers": [len(act_list[i]) for i in range(len(act_list))],
                                    "activations": act_list,
                                }
                            )
                        )

                        await websocket.send(json.dumps({"type": "move", "index": move, "player": -1}))

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-e", "--epochs", type=int, default=20)
    parser.add_argument("-b", "--batch-size", type=int, default=64)
    parser.add_argument("-s", "--samples", type=int, default=5000)
    args = parser.parse_args()

    if args.mode == "train":
        train(args.epochs, args.batch_size, args.samples)
    else:
        try:
            asyncio.run(play())
        except KeyboardInterrupt:
            pass
