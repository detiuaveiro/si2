import asyncio
import heapq
import json
import logging
import random

from base_agent import BaseAgent
from sklearn.ensemble import RandomForestClassifier


class HybridMLAgent(BaseAgent):
    """
    A Hybrid Agent that uses a Machine Learning model to predict the geometry of unknown
    space (World Modeling) using Local Neighborhood Features, and an A* Planner to navigate.
    """

    def __init__(self, server_uri="ws://localhost:8765"):
        super().__init__(server_uri)
        self.known_free = set()
        self.known_walls = set()
        self.visited = set()

        self.cached_path = []
        self.last_train_size = 0

        self.ml_model = RandomForestClassifier(n_estimators=20, random_state=42)
        self.is_ml_trained = False

    def reset_memory(self):
        self.known_free.clear()
        self.known_walls.clear()
        self.visited.clear()
        self.cached_path = []
        self.last_train_size = 0
        self.is_ml_trained = False
        logging.info("Hybrid Agent wiped memory for new simulation.")

    def _get_features(self, target_x, target_y):
        """
        Extracts the 'Local Neighborhood' around a target coordinate.
        Returns a list of 8 integers representing the known state of adjacent tiles.
        1 = Known Floor, 0 = Known Wall, -1 = Unknown.
        """
        features = []
        neighbors = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

        for dx, dy in neighbors:
            nx, ny = target_x + dx, target_y + dy

            if nx < 0 or nx >= self.current_state["width"] or ny < 0 or ny >= self.current_state["height"]:
                features.append(0)  # Map boundaries act like walls
            elif (nx, ny) in self.known_free:
                features.append(1)
            elif (nx, ny) in self.known_walls:
                features.append(0)
            else:
                features.append(-1)  # Unknown territory

        return features

    def _update_internal_map(self):
        x, y = self.current_state["position"]
        self.known_free.add((x, y))
        self.visited.add((x, y))

        width = self.current_state["width"]
        height = self.current_state["height"]
        valid_actions = self.current_state["valid_actions"]

        if y > 0:
            if "N" in valid_actions:
                self.known_free.add((x, y - 1))
            else:
                self.known_walls.add((x, y - 1))
        if y < height - 1:
            if "S" in valid_actions:
                self.known_free.add((x, y + 1))
            else:
                self.known_walls.add((x, y + 1))
        if x < width - 1:
            if "E" in valid_actions:
                self.known_free.add((x + 1, y))
            else:
                self.known_walls.add((x + 1, y))
        if x > 0:
            if "W" in valid_actions:
                self.known_free.add((x - 1, y))
            else:
                self.known_walls.add((x - 1, y))

        current_knowledge_size = len(self.known_free) + len(self.known_walls)
        if current_knowledge_size > self.last_train_size + 5:
            self._train_world_model()
            self.last_train_size = current_knowledge_size

    def _train_world_model(self):
        if not self.known_free or not self.known_walls:
            return

        X, y = [], []

        for fx, fy in self.known_free:
            X.append(self._get_features(fx, fy))
            y.append(1)

        for wx, wy in self.known_walls:
            X.append(self._get_features(wx, wy))
            y.append(0)

        self.ml_model.fit(X, y)
        self.is_ml_trained = True

    def _get_movement_cost(self, x, y):
        if (x, y) in self.known_walls:
            return float("inf")
        if (x, y) in self.known_free:
            return 1.0

        if self.is_ml_trained:
            # FIX: Ensure we use the 8-feature array for predictions
            features = self._get_features(x, y)
            prediction = self.ml_model.predict([features])[0]

            if prediction == 1:
                return 1.5
            else:
                return 4.0

        return 1.5

    def _heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    current, direction = came_from[current]
                    path.append(direction)
                path.reverse()
                return path

            cx, cy = current
            neighbors = [(cx, cy - 1, "N"), (cx, cy + 1, "S"), (cx + 1, cy, "E"), (cx - 1, cy, "W")]

            for nx, ny, direction in neighbors:
                if nx < 0 or nx >= self.current_state["width"] or ny < 0 or ny >= self.current_state["height"]:
                    continue

                move_cost = self._get_movement_cost(nx, ny)
                if move_cost == float("inf"):
                    continue

                tentative_g = g_score[current] + move_cost
                neighbor_pos = (nx, ny)

                if tentative_g < g_score.get(neighbor_pos, float("inf")):
                    came_from[neighbor_pos] = (current, direction)
                    g_score[neighbor_pos] = tentative_g
                    f_score[neighbor_pos] = tentative_g + self._heuristic(neighbor_pos, goal)
                    heapq.heappush(open_set, (f_score[neighbor_pos], neighbor_pos))

        return []

    def _get_next_action_from_cache(self):
        if not self.cached_path:
            return None

        next_step = self.cached_path[0]
        if next_step not in self.current_state["valid_actions"]:
            self.cached_path = []
            return None

        return self.cached_path.pop(0)

    async def deliberate_maze(self):
        self._update_internal_map()

        action = self._get_next_action_from_cache()
        if action:
            return action

        target = tuple(self.current_state["target"])
        current_pos = tuple(self.current_state["position"])

        self.cached_path = self._a_star(current_pos, target)

        if self.cached_path:
            return self.cached_path.pop(0)

        valid = self.current_state.get("valid_actions", [])
        return random.choice(valid) if valid else None

    async def deliberate_room(self):
        self._update_internal_map()

        action = self._get_next_action_from_cache()
        if action:
            return action

        current_pos = tuple(self.current_state["position"])
        w, h = self.current_state["width"], self.current_state["height"]

        frontiers = set()
        for vx, vy in self.visited:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = vx + dx, vy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if (nx, ny) not in self.visited and (nx, ny) not in self.known_walls:
                        frontiers.add((nx, ny))

        if not frontiers:
            valid = self.current_state.get("valid_actions", [])
            return random.choice(valid) if valid else None

        frontier_list = list(frontiers)
        frontier_list.sort(key=lambda t: self._heuristic(current_pos, t))

        for target in frontier_list[:5]:
            self.cached_path = self._a_star(current_pos, target)
            if self.cached_path:
                return self.cached_path.pop(0)

        valid = self.current_state.get("valid_actions", [])
        return random.choice(valid) if valid else None

    async def send_telemetry(self, websocket):
        visited_list = [f"{x},{y}" for x, y in self.visited]
        probs = {"N": 0.0, "S": 0.0, "E": 0.0, "W": 0.0}
        x, y = self.current_state["position"]
        directions = {"N": (x, y - 1), "S": (x, y + 1), "E": (x + 1, y), "W": (x - 1, y)}

        for dir_key, (nx, ny) in directions.items():
            if dir_key in self.current_state["valid_actions"]:
                probs[dir_key] = 1.0
            elif (nx, ny) in self.known_walls:
                probs[dir_key] = 0.0
            elif self.is_ml_trained:
                try:
                    # FIX: Ensure we use the 8-feature array for UI probabilities
                    features = self._get_features(nx, ny)
                    p = self.ml_model.predict_proba([features])[0]
                    free_idx = list(self.ml_model.classes_).index(1)
                    probs[dir_key] = float(p[free_idx])
                except ValueError:
                    probs[dir_key] = 0.5
            else:
                probs[dir_key] = 0.5

        await websocket.send(json.dumps({"action": "telemetry", "data": {"visited": visited_list, "current_probs": probs}}))


if __name__ == "__main__":
    agent = HybridMLAgent()
    asyncio.run(agent.run())
