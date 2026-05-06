import argparse, os, sys, numpy as np, requests
from tqdm import tqdm
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8003")

class TQDMCallback(keras.callbacks.Callback):
    def on_train_begin(self, logs=None): self.pbar = tqdm(total=self.params['epochs'], desc="Training", unit="epoch")
    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs: self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})
    def on_train_end(self, logs=None): self.pbar.close()

def reset_backend(): return requests.get(f"{BACKEND_URL}/reset").json()
def move_backend(pos): return requests.post(f"{BACKEND_URL}/move", json=list(pos)).json()
def get_local_backend(pos): return requests.post(f"{BACKEND_URL}/local", json=list(pos)).json()["local"]

def generate(num=100):
    states, actions = [], []
    print(f"Generating Maze data from {num} mazes...")
    for _ in tqdm(range(num), desc="Simulating"):
        data = reset_backend(); path = data["shortest_path"]
        if path:
            curr, goal = [0, 0], [9, 9]
            for a in path:
                states.append(get_local_backend(curr) + [goal[0]-curr[0], goal[1]-curr[1]])
                actions.append(a)
                if a==0: curr[0]-=1
                elif a==1: curr[0]+=1
                elif a==2: curr[1]-=1
                elif a==3: curr[1]+=1
                move_backend(curr)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data"); os.makedirs(data_dir, exist_ok=True)
    np.save(os.path.join(data_dir, "X.npy"), np.array(states)); np.save(os.path.join(data_dir, "y.npy"), np.array(actions))

def train(epochs=20, batch_size=32, force_gen=False):
    base_dir = os.path.dirname(os.path.abspath(__file__)); x_path = os.path.join(base_dir, "data/X.npy")
    if force_gen or not os.path.exists(x_path): generate()
    X, y = np.load(x_path), np.load(os.path.join(base_dir, "data/y.npy"))
    y_oh = keras.utils.to_categorical(y, 4)
    model = keras.Sequential([keras.layers.Input(shape=(11,)), keras.layers.Dense(64, activation="relu"), keras.layers.Dense(64, activation="relu"), keras.layers.Dense(4, activation="softmax")])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    print(f"Training for {epochs} epochs...")
    model.fit(X, y_oh, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0, callbacks=[TQDMCallback()])
    model.save(os.path.join(base_dir, "model.keras"))

def play(size=10):
    base_dir = os.path.dirname(os.path.abspath(__file__)); m_path = os.path.join(base_dir, "model.keras")
    if not os.path.exists(m_path): print("Train first."); return
    model = keras.models.load_model(m_path)
    reset_backend(); curr, goal = [0, 0], [size-1, size-1]
    move_backend(curr)
    for step in range(100):
        if curr == goal: print(f"Goal reached in {step} steps!"); return
        state = np.array([get_local_backend(curr) + [goal[0]-curr[0], goal[1]-curr[1]]])
        move = np.argmax(model.predict(state, verbose=0)[0])
        if move==0: curr[0]-=1
        elif move==1: curr[0]+=1
        elif move==2: curr[1]-=1
        elif move==3: curr[1]+=1
        move_backend(curr)
        import time; time.sleep(0.1) # Slow down for visualization
    print("Failed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maze Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    tr = parser.add_argument_group("Training Options")
    tr.add_argument("-e", "--epochs", type=int, default=20); tr.add_argument("-b", "--batch-size", type=int, default=32); tr.add_argument("-f", "--force-generate", action="store_true")
    pl = parser.add_argument_group("Playing Options")
    pl.add_argument("-s", "--size", type=int, default=10); args = parser.parse_args()
    if args.mode == "train": train(args.epochs, args.batch_size, args.force_generate)
    else: play(args.size)
