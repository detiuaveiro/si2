import argparse
import asyncio
import heapq
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


class MazeSimulator:
    def __init__(self, size=10):
        self.size = size

    def generate_data(self, num_samples=1000):
        X_pure, y_pure = [], []
        X_hybrid, y_hybrid = [], []

        for _ in tqdm(range(num_samples // 10), desc="Generating Maze Data"):
            grid = np.zeros((self.size, self.size), dtype=int)
            for _ in range(int(self.size * self.size * 0.2)):
                grid[np.random.randint(0, self.size), np.random.randint(0, self.size)] = 1
            
            start, target = (0, 0), (self.size - 1, self.size - 1)
            grid[start] = 0
            grid[target] = 0
            
            path = self._a_star(grid, start, target)
            if path:
                curr = list(start)
                for move in path:
                    state = self._get_local_state(grid, curr, target)
                    X_pure.append(state)
                    y_pure.append(move)
                    
                    neighbors = self._get_all_neighbors(grid, curr)
                    for nx, ny, is_free in neighbors:
                        X_hybrid.append(self._get_local_grid(grid, [nx, ny]))
                        y_hybrid.append(1 if is_free else 0)
                    
                    if move == 0: curr[0] -= 1
                    elif move == 1: curr[1] += 1
                    elif move == 2: curr[0] += 1
                    elif move == 3: curr[1] -= 1
        
        return np.array(X_pure), np.array(y_pure), np.array(X_hybrid), np.array(y_hybrid)

    def _get_local_state(self, grid, pos, target):
        x, y = pos
        res = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if 0 <= i < self.size and 0 <= j < self.size:
                    res.append(float(grid[i, j]))
                else:
                    res.append(1.0)
        res.extend([float(target[0] - x), float(target[1] - y)])
        return res

    def _get_local_grid(self, grid, pos):
        x, y = pos
        res = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if 0 <= i < self.size and 0 <= j < self.size:
                    res.append(float(grid[i, j]))
                else:
                    res.append(1.0)
        return res

    def _get_all_neighbors(self, grid, pos):
        x, y = pos
        res = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                res.append((nx, ny, grid[nx, ny] == 0))
        return res

    def _a_star(self, grid, start, target):
        q = [(0, start)]
        visited = set()
        parent = {}
        g_score = {start: 0}
        
        while q:
            _, curr = heapq.heappop(q)
            if curr == target:
                path = []
                while curr != start:
                    prev = parent[curr]
                    if prev[0] > curr[0]: path.append(0)
                    elif prev[1] < curr[1]: path.append(1)
                    elif prev[0] < curr[0]: path.append(2)
                    elif prev[1] > curr[1]: path.append(3)
                    curr = prev
                return path[::-1]
            
            visited.add(curr)
            cx, cy = curr
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.size and 0 <= ny < self.size and grid[nx, ny] == 0 and (nx, ny) not in visited:
                    tentative_g = g_score[curr] + 1
                    if tentative_g < g_score.get((nx, ny), float('inf')):
                        parent[(nx, ny)] = curr
                        g_score[(nx, ny)] = tentative_g
                        f = tentative_g + abs(nx - target[0]) + abs(ny - target[1])
                        heapq.heappush(q, (f, (nx, ny)))
        return None


def train(epochs=20, batch_size=32, samples=1000, mode="pure"):
    sim = MazeSimulator()
    X_p, y_p, X_h, y_h = sim.generate_data(num_samples=samples)
    
    if mode == "pure":
        X, y = X_p, y_p
        y_oh = keras.utils.to_categorical(y, 4)
        model = keras.Sequential([
            keras.layers.Input(shape=(11,)),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.Dense(4, activation="softmax")
        ])
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        model.fit(X, y_oh, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0, callbacks=[TQDMCallback()])
        model.save("model_pure.keras")
    else:
        X, y = X_h, y_h
        model = keras.Sequential([
            keras.layers.Input(shape=(9,)),
            keras.layers.Dense(32, activation="relu"),
            keras.layers.Dense(1, activation="sigmoid")
        ])
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=0, callbacks=[TQDMCallback()])
        model.save("model_hybrid.keras")


async def play(mode="pure"):
    m_path = f"model_{mode}.keras"
    if not os.path.exists(m_path):
        print(f"Train {mode} model first.")
        return
    model = keras.models.load_model(m_path)
    
    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"Connected to backend. Playing in {mode} mode...")
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "state":
                    if data.get("done"):
                        print("Goal reached!")
                        await asyncio.sleep(2)
                        await websocket.send(json.dumps({"type": "reset"}))
                        continue
                    
                    grid = np.array(data.get("grid"))
                    pos = data.get("agent_pos")
                    target = data.get("target")
                    size = grid.shape[0]
                    
                    if mode == "pure":
                        state = []
                        for i in range(pos[0]-1, pos[0]+2):
                            for j in range(pos[1]-1, pos[1]+2):
                                if 0 <= i < size and 0 <= j < size: state.append(float(grid[i, j]))
                                else: state.append(1.0)
                        state.extend([float(target[0]-pos[0]), float(target[1]-pos[1])])
                        
                        prediction = model.predict(np.array([state]), verbose=0)
                        action = int(np.argmax(prediction[0]))
                    else:
                        action = hybrid_deliberate(model, grid, pos, target)
                    
                    await websocket.send(json.dumps({"type": "move", "action": action}))
                    await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")


def hybrid_deliberate(model, grid, pos, target):
    size = grid.shape[0]
    q = [(0, tuple(pos))]
    parent = {}
    g_score = {tuple(pos): 0}
    
    while q:
        _, curr = heapq.heappop(q)
        if list(curr) == target:
            path = []
            while tuple(curr) != tuple(pos):
                prev = parent[tuple(curr)]
                if prev[0] > curr[0]: p = 0
                elif prev[1] < curr[1]: p = 1
                elif prev[0] < curr[0]: p = 2
                elif prev[1] > curr[1]: p = 3
                path.append(p); curr = prev
            return path[-1]
        
        cx, cy = curr
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = cx+dx, cy+dy
            if 0<=nx<size and 0<=ny<size:
                local = []
                for i in range(nx-1, nx+2):
                    for j in range(ny-1, ny+2):
                        if 0<=i<size and 0<=j<size: local.append(float(grid[i,j]))
                        else: local.append(1.0)
                
                prob_free = model.predict(np.array([local]), verbose=0)[0][0]
                cost = 1.0 if prob_free > 0.8 else 5.0 if prob_free > 0.5 else 100.0
                if grid[nx, ny] == 1: cost = 1000.0
                
                tentative_g = g_score[tuple(curr)] + cost
                if tentative_g < g_score.get((nx, ny), float('inf')):
                    parent[(nx, ny)] = curr
                    g_score[(nx, ny)] = tentative_g
                    f = tentative_g + abs(nx - target[0]) + abs(ny - target[1])
                    heapq.heappush(q, (f, (nx, ny)))
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maze Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-a", "--agent", choices=["pure", "hybrid"], default="pure")
    parser.add_argument("-e", "--epochs", type=int, default=20)
    parser.add_argument("-s", "--samples", type=int, default=1000)
    args = parser.parse_args()

    if args.mode == "train":
        train(epochs=args.epochs, mode=args.agent, samples=args.samples)
    else:
        try:
            asyncio.run(play(mode=args.agent))
        except KeyboardInterrupt:
            pass
