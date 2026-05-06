import argparse, os, sys, numpy as np, requests
from tqdm import tqdm
from collections import deque
import time

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

class TQDMCallback(keras.callbacks.Callback):
    def on_train_begin(self, logs=None): self.pbar = tqdm(total=self.params['epochs'], desc="Training", unit="epoch")
    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs: self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})
    def on_train_end(self, logs=None): self.pbar.close()

def reset_backend(size=10):
    try: return requests.get(f"{BACKEND_URL}/reset", params={"size": size}).json()
    except: print("Start backend first."); sys.exit(1)

def step_backend(action):
    return requests.post(f"{BACKEND_URL}/step", params={"action": int(action)}).json()

def get_visual_state(size, snake, food):
    state = np.zeros((size, size, 3), dtype=np.float32)
    for b in snake[1:]: state[b[0], b[1], 0] = 1.0
    state[snake[0][0], snake[0][1], 1] = 1.0
    state[food[0], food[1], 2] = 1.0
    return state

def get_expert_action(size, snake, food):
    q = deque([(tuple(snake[0]), [])]); v = set(tuple(p) for p in snake)
    while q:
        (x, y), p = q.popleft()
        if [x, y] == food: return p[0]
        for dx, dy, a in [(-1,0,0),(1,0,1),(0,-1,2),(0,1,3)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<size and 0<=ny<size and (nx,ny) not in v:
                v.add((nx,ny)); q.append(((nx,ny), p+[a]))
    return None

def generate(episodes=50):
    states, actions, size = [], [], 10
    print(f"Generating Snake data from {episodes} episodes...")
    for _ in tqdm(range(episodes), desc="Simulating"):
        data = reset_backend(size)
        snake, food = data["snake"], data["food"]
        done = False
        while not done:
            a = get_expert_action(size, snake, food)
            if a is None: break
            states.append(get_visual_state(size, snake, food))
            actions.append(a)
            data = step_backend(a)
            snake, food, done = data["snake"], data["food"], data["done"]
            if len(states) > 10000: break
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data"); os.makedirs(data_dir, exist_ok=True)
    np.save(os.path.join(data_dir, "X.npy"), np.array(states))
    np.save(os.path.join(data_dir, "y.npy"), np.array(actions))

def train(epochs=20, batch_size=32, force_gen=False):
    base_dir = os.path.dirname(os.path.abspath(__file__)); x_path = os.path.join(base_dir, "data/X.npy")
    if force_gen or not os.path.exists(x_path): generate()
    X, y = np.load(x_path), np.load(os.path.join(base_dir, "data/y.npy"))
    y_oh = keras.utils.to_categorical(y, 4)
    model = keras.Sequential([
        keras.layers.Input(shape=(10, 10, 3)),
        keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
        keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
        keras.layers.Flatten(),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(4, activation="softmax")
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    print(f"Training for {epochs} epochs...")
    model.fit(X, y_oh, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0, callbacks=[TQDMCallback()])
    model.save(os.path.join(base_dir, "model.keras"))

def play(size=10):
    base_dir = os.path.dirname(os.path.abspath(__file__)); m_path = os.path.join(base_dir, "model.keras")
    if not os.path.exists(m_path): print("Train first."); return
    model = keras.models.load_model(m_path)
    data = reset_backend(size)
    snake, food = data["snake"], data["food"]
    score = 0
    for step in range(200):
        s_vis = get_visual_state(size, snake, food)
        pred = model.predict(s_vis.reshape(1, size, size, 3), verbose=0)[0]
        data = step_backend(np.argmax(pred))
        snake, food, done, r = data["snake"], data["food"], data["done"], data["reward"]
        if r > 0: score += 1
        if done: break
        time.sleep(0.1) # Smooth visualization
    print(f"Score: {score}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snake Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    tr = parser.add_argument_group("Training Options")
    tr.add_argument("-e", "--epochs", type=int, default=20); tr.add_argument("-b", "--batch-size", type=int, default=32); tr.add_argument("-f", "--force-generate", action="store_true")
    pl = parser.add_argument_group("Playing Options")
    pl.add_argument("-s", "--size", type=int, default=10); args = parser.parse_args()
    if args.mode == "train": train(args.epochs, args.batch_size, args.force_generate)
    else: play(args.size)
