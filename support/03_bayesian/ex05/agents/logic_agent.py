import asyncio
import json

from base_agent import BaseAgent


class DFSAgent(BaseAgent):
    def __init__(self, server_uri="ws://localhost:8765"):
        super().__init__(server_uri)
        self.reset_memory()

    def reset_memory(self):
        self.visited = set()
        self.path_stack = []

    def _get_next_pos(self, pos, direction):
        x, y = pos
        return {
            "N": f"{x},{y - 1}",
            "S": f"{x},{y + 1}",
            "E": f"{x + 1},{y}",
            "W": f"{x - 1},{y}",
        }[direction]

    def _get_opposite(self, direction):
        return {"N": "S", "S": "N", "E": "W", "W": "E"}.get(direction)

    async def deliberate_maze(self):
        return self._dfs_step()

    async def deliberate_room(self):
        return self._dfs_step()

    def _dfs_step(self):
        pos = self.current_state.get("position")
        valid_actions = self.current_state.get("valid_actions", [])
        self.visited.add(f"{pos[0]},{pos[1]}")

        if not valid_actions:
            return None

        # 1. Unvisited adjacent cell
        for action in valid_actions:
            if self._get_next_pos(pos, action) not in self.visited:
                self.path_stack.append(action)
                return action

        # 2. Backtrack on dead end
        if self.path_stack:
            return self._get_opposite(self.path_stack.pop())

        return valid_actions[0]

    async def send_telemetry(self, websocket):
        await websocket.send(
            json.dumps(
                {
                    "action": "telemetry",
                    "data": {
                        "visited": list(self.visited),
                        "current_probs": {"N": 0.25, "S": 0.25, "E": 0.25, "W": 0.25},
                    },
                }
            )
        )


if __name__ == "__main__":
    agent = DFSAgent()
    asyncio.run(agent.run())
