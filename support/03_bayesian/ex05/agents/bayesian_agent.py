import asyncio
import json
import logging
import random

from base_agent import BaseAgent


class BayesianAgent(BaseAgent):
    def __init__(self, server_uri="ws://localhost:8765"):
        super().__init__(server_uri)
        self.w_target = 3.0
        self.p_backtrack = 0.01
        self.p_deadend = 0.01
        self.reset_memory()

    def reset_memory(self):
        self.belief_state = {}
        self.history = []
        self.current_probs = {"N": 0, "S": 0, "E": 0, "W": 0}

    # --- Math Helpers ---
    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _get_next_pos(self, pos, direction):
        x, y = pos
        return {"N": [x, y - 1], "S": [x, y + 1], "E": [x + 1, y], "W": [x - 1, y]}[
            direction
        ]

    def _get_key(self, pos):
        return f"{pos[0]},{pos[1]}"

    def _normalize(self, probs_dict):
        total = sum(probs_dict.values())
        if total > 0:
            for k in probs_dict:
                probs_dict[k] /= total
        return probs_dict

    def _get_opposite(self, direction):
        return {"N": "S", "S": "N", "E": "W", "W": "E"}.get(direction)

    # --- Heuristics ---
    def calculate_maze_prior(self, pos, valid_actions, target, start_pos):
        probs = {a: 1.0 for a in valid_actions}
        if target and start_pos:
            c_target_dist = self._manhattan_distance(pos, target)
            c_start_dist = self._manhattan_distance(pos, start_pos)

            for a in valid_actions:
                n_pos = self._get_next_pos(pos, a)
                if self._manhattan_distance(n_pos, target) < c_target_dist:
                    probs[a] += 0.2
                if self._manhattan_distance(n_pos, target) > c_target_dist:
                    probs[a] = max(0.1, probs[a] - 0.2)
                if self._manhattan_distance(n_pos, start_pos) > c_start_dist:
                    probs[a] += 0.2
                if self._manhattan_distance(n_pos, start_pos) < c_start_dist:
                    probs[a] = max(0.1, probs[a] - 0.2)
        return self._normalize(probs)

    def calculate_room_prior(self, pos, valid_actions):
        """Room heuristic: Double the probability of actions leading to unvisited cells."""
        probs = {"N": 0.0, "S": 0.0, "E": 0.0, "W": 0.0}
        for a in valid_actions:
            next_pos_key = self._get_key(self._get_next_pos(pos, a))
            # Give a heavy boost to exploring the unknown
            probs[a] = 2.0 if next_pos_key not in self.belief_state else 1.0
        return self._normalize(probs)

    # --- Core Logic ---
    async def deliberate_maze(self):
        return self._core_logic(is_maze=True)

    async def deliberate_room(self):
        return self._core_logic(is_maze=False)

    def _core_logic(self, is_maze):
        pos = self.current_state.get("position")
        valid_actions = self.current_state.get("valid_actions", [])
        pos_key = self._get_key(pos)

        if not valid_actions:
            return None

        # 1. Initialize cell memory with the correct heuristic
        if pos_key not in self.belief_state:
            if is_maze:
                target = self.current_state.get("target")
                start = self.current_state.get("start")
                self.belief_state[pos_key] = self.calculate_maze_prior(
                    pos, valid_actions, target, start
                )
            else:
                self.belief_state[pos_key] = self.calculate_room_prior(
                    pos, valid_actions
                )

        # 2. Dead End Penalties
        if len(valid_actions) == 1 and self.history:
            prev_pos_key, prev_action = self.history[-1]
            if prev_pos_key in self.belief_state:
                self.belief_state[prev_pos_key][prev_action] *= self.p_deadend
                self.belief_state[prev_pos_key] = self._normalize(
                    self.belief_state[prev_pos_key]
                )

        # 3. Temporary Backtrack Penalty
        current_probs = self.belief_state[pos_key].copy()
        if self.history:
            backtrack = self._get_opposite(self.history[-1][1])
            if backtrack in current_probs and current_probs[backtrack] > 0:
                current_probs[backtrack] *= self.p_backtrack

        self.current_probs = self._normalize(current_probs)

        # 4. Action Selection
        actions, weights = (
            list(self.current_probs.keys()),
            list(self.current_probs.values()),
        )
        if sum(weights) == 0:
            weights = [1.0 if a in valid_actions else 0.0 for a in actions]

        chosen_action = random.choices(actions, weights=weights, k=1)[0]
        self.history.append((pos_key, chosen_action))

        return chosen_action

    async def send_telemetry(self, websocket):
        """Dispatches the currently calculated probabilities to the UI."""
        await websocket.send(
            json.dumps(
                {
                    "action": "telemetry",
                    "data": {
                        "visited": list(self.belief_state.keys()),
                        "current_probs": getattr(self, "current_probs", {}),
                    },
                }
            )
        )


if __name__ == "__main__":
    agent = BayesianAgent()
    asyncio.run(agent.run())
