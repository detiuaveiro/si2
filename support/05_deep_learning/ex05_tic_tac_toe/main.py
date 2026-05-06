import argparse, os, sys, numpy as np, requests
from tqdm import tqdm
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8002")

class TQDMCallback(keras.callbacks.Callback):
    def on_train_begin(self, logs=None): self.pbar = tqdm(total=self.params['epochs'], desc="Training", unit="epoch")
    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs: self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})
    def on_train_end(self, logs=None): self.pbar.close()

def reset_backend(): return requests.get(f"{BACKEND_URL}/reset").json()["board"]
def move_backend(idx, p): return requests.post(f"{BACKEND_URL}/move", params={"index": int(idx), "player": int(p)}).json()

def check_winner_local(b):
    for i in range(3):
        if abs(sum(b[i*3:(i+1)*3])) == 3: return b[i*3]
        if abs(sum(b[i::3])) == 3: return b[i]
    if abs(sum(b[0::4])) == 3: return b[0]
    if abs(sum(b[2:7:2])) == 3: return b[2]
    if 0 not in b: return 0
    return None

_memo = {}
def minimax(b, p):
    sk = (tuple(b), p)
    if sk in _memo: return _memo[sk]
    w = check_winner_local(b)
    if w is not None: return w * p, None
    bs, bm = -2, None
    for i in range(9):
        if b[i] == 0:
            b[i] = p; s, _ = minimax(b, -p); s = -s; b[i] = 0
            if s > bs: bs, bm = s, i
    _memo[sk] = (bs, bm); return bs, bm

def gen(num=5000):
    states, actions = [], []
    print(f"Generating Tic-Tac-Toe data ({num} samples)...")
    for _ in tqdm(range(num), desc="Simulating"):
        board = [0]*9; player = 1
        for _ in range(np.random.randint(0, 7)):
            empty = [i for i,x in enumerate(board) if x==0]
            if not empty: break
            board[np.random.choice(empty)] = player; player *= -1
            if check_winner_local(board) is not None: board, player = [0]*9, 1; break
        _, move = minimax(board, player)
        if move is not None: states.append([x * player for x in board]); actions.append(move)
    base = os.path.dirname(os.path.abspath(__file__)); d_dir = os.path.join(base, "data"); os.makedirs(d_dir, exist_ok=True)
    np.save(os.path.join(d_dir, "X.npy"), np.array(states)); np.save(os.path.join(d_dir, "y.npy"), np.array(actions))

def train(epochs=20, batch_size=64, force_gen=False):
    base_dir = os.path.dirname(os.path.abspath(__file__)); x_path = os.path.join(base_dir, "data/X.npy")
    if force_gen or not os.path.exists(x_path): gen()
    X, y = np.load(x_path), np.load(os.path.join(base_dir, "data/y.npy"))
    y_oh = keras.utils.to_categorical(y, 9)
    model = keras.Sequential([keras.layers.Input(shape=(9,)), keras.layers.Dense(128, activation="relu"), keras.layers.Dense(128, activation="relu"), keras.layers.Dense(9, activation="softmax")])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    print(f"Training for {epochs} epochs...")
    model.fit(X, y_oh, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0, callbacks=[TQDMCallback()])
    model.save(os.path.join(base_dir, "model.keras"))


def play():
    base = os.path.dirname(os.path.abspath(__file__)); mp = os.path.join(base, "model.keras")
    if not os.path.exists(mp): print("Train first."); return
    model = keras.models.load_model(mp)
    board = reset_backend(); player = 1
    winner = None
    while winner is None:
        if player == 1:
            m = np.argmax(model.predict(np.array([board]), verbose=0)[0])
            if board[m] != 0: m = [i for i,x in enumerate(board) if x==0][0]
        else:
            m = np.random.choice([i for i,x in enumerate(board) if x==0])
        
        res = move_backend(m, player)
        board, winner = res["board"], res["winner"]
        player *= -1
    print("Winner:", "Agent" if winner==1 else "Opponent" if winner==-1 else "Draw")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    tr = parser.add_argument_group("Training Options")
    tr.add_argument("-e", "--epochs", type=int, default=20); tr.add_argument("-b", "--batch-size", type=int, default=64); tr.add_argument("-f", "--force-generate", action="store_true"); tr.add_argument("-n", "--num-samples", type=int, default=5000)
    args = parser.parse_args()
    if args.mode == "train":
        num = args.num_samples
        train(args.epochs, args.batch_size, args.force_generate)
    else: play()
