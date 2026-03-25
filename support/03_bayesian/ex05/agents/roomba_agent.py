import asyncio
import json
import logging

from base_agent import BaseAgent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - ROOMBA - %(levelname)s - %(message)s"
)


class RoombaAgent(BaseAgent):
    """
    A reactive agent mimicking a robot vacuum.
    Uses Spiral Sweep, Edge Cleaning, and Cross-Room Bounces to escape loops.
    """

    def __init__(self, server_uri="ws://localhost:8765"):
        super().__init__(server_uri)
        # Pre-calculate turn directions for easy reference
        self.right_turns = {"N": "E", "E": "S", "S": "W", "W": "N"}
        self.left_turns = {"N": "W", "W": "S", "S": "E", "E": "N"}
        self.back_turns = {"N": "S", "S": "N", "E": "W", "W": "E"}
        self.reset_memory()

    def reset_memory(self):
        """Initializes the Roomba's internal mechanical state."""
        self.mode = "SPIRAL"
        self.visited = set()
        self.boredom = 0  # Tracks how long we've been stuck on old tiles

        # Spiral Sweep Variables
        self.dirs = ["N", "E", "S", "W"]
        self.dir_idx = 0
        self.leg_target = 1
        self.legs_completed = 0
        self.steps_taken = 0

        # Edge Cleaning Variables
        self.facing = "N"

    async def deliberate_maze(self):
        return self._clean()

    async def deliberate_room(self):
        return self._clean()

    def _clean(self):
        valid_actions = self.current_state.get("valid_actions", [])
        pos = self.current_state.get("position")
        pos_key = f"{pos[0]},{pos[1]}"

        if not valid_actions:
            return None

        # --- LOOP DETECTION (The Boredom Meter) ---
        if pos_key in self.visited:
            self.boredom += 1
        else:
            self.boredom = 0
            self.visited.add(pos_key)

        # If we loop an island too many times, cross the room!
        if self.boredom > 6 and self.mode == "EDGE":
            logging.info("Bored of this loop! Bouncing across the room.")
            self.mode = "BOUNCE"
            self.boredom = 0
            # Turn Left (away from the right-hand wall) to break the orbit
            self.facing = self.left_turns[self.facing]

        # --- MODE 1: EXPANDING SPIRAL SWEEP ---
        if self.mode == "SPIRAL":
            desired_dir = self.dirs[self.dir_idx]

            # Hit a wall -> permanent switch to edge cleaning
            if desired_dir not in valid_actions:
                self.mode = "EDGE"
                self.facing = valid_actions[0]
                return self._edge_follow(valid_actions)

            self.steps_taken += 1
            if self.steps_taken == self.leg_target:
                self.steps_taken = 0
                self.dir_idx = (self.dir_idx + 1) % 4
                self.legs_completed += 1
                if self.legs_completed == 2:
                    self.legs_completed = 0
                    self.leg_target += 1

            self.facing = desired_dir
            return desired_dir

        # --- MODE 2: EDGE CLEANING (Right-Hand Rule) ---
        elif self.mode == "EDGE":
            return self._edge_follow(valid_actions)

        # --- MODE 3: CROSS-ROOM BOUNCE ---
        elif self.mode == "BOUNCE":
            if self.facing in valid_actions:
                return self.facing  # Keep going straight
            else:
                # We hit a new wall across the room! Go back to edge cleaning.
                self.mode = "EDGE"
                return self._edge_follow(valid_actions)

    def _edge_follow(self, valid_actions):
        """Executes the Right-Hand Rule to hug walls."""
        right = self.right_turns[self.facing]
        left = self.left_turns[self.facing]
        back = self.back_turns[self.facing]

        # Priority: Right > Straight > Left > Back
        if right in valid_actions:
            self.facing = right
            return right
        elif self.facing in valid_actions:
            return self.facing
        elif left in valid_actions:
            self.facing = left
            return left
        else:
            self.facing = back
            return back

    async def send_telemetry(self, websocket):
        """Sends the visited map and facing direction to the UI."""
        probs = {d: (1.0 if d == self.facing else 0.0) for d in ["N", "S", "E", "W"]}
        await websocket.send(
            json.dumps(
                {
                    "action": "telemetry",
                    "data": {"visited": list(self.visited), "current_probs": probs},
                }
            )
        )


if __name__ == "__main__":
    agent = RoombaAgent()
    asyncio.run(agent.run())
