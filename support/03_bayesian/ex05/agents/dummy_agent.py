import asyncio
import random

from base_agent import BaseAgent


class DummyAgent(BaseAgent):
    """A purely random agent that works in both Mazes and Rooms."""

    async def deliberate_maze(self):
        return self._random_move()

    async def deliberate_room(self):
        return self._random_move()

    def _random_move(self):
        valid_actions = self.current_state.get("valid_actions", [])
        return random.choice(valid_actions) if valid_actions else None


if __name__ == "__main__":
    agent = DummyAgent()
    asyncio.run(agent.run())
