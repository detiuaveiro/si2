import asyncio
import json
import logging

import websockets

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - AGENT - %(levelname)s - %(message)s"
)


class BaseAgent:
    """
    Abstract base class for simulation agents.
    Handles all websocket communications, state updates, routing, and UI telemetry.
    Subclasses MUST implement the deliberate_maze and deliberate_room methods.
    """

    def __init__(self, server_uri="ws://localhost:8765"):
        self.server_uri = server_uri
        self.current_state = None

    async def run(self):
        """Main connection loop. Do not override this unless modifying network protocols."""
        try:
            async with websockets.connect(self.server_uri) as websocket:
                await websocket.send(json.dumps({"client": "agent"}))
                logging.info(f"Connected to {self.server_uri}")

                async for message in websocket:
                    data = json.loads(message)

                    if data.get("type") == "state":
                        self.current_state = data

                        if self.current_state.get("objective_reached"):
                            if not getattr(self, "idle_logged", False):
                                # FIX 2: Force one final thought process and telemetry broadcast
                                # so the UI's memory map updates the winning tile before going to sleep.
                                await self.deliberate()
                                await self.send_telemetry(websocket)

                                logging.info("Objective reached. Idling...")
                                self.idle_logged = True
                            continue
                        else:
                            self.idle_logged = False

                        # Ask the subclass for the next move
                        action = await self.deliberate()

                        if action:
                            # FIX 1: Send telemetry BEFORE moving.
                            # This guarantees the agent's thought process is rendered by the frontend
                            # right before the physical movement happens, fixing the visual lag.
                            await self.send_telemetry(websocket)
                            await websocket.send(
                                json.dumps({"action": "move", "direction": action})
                            )

                            await asyncio.sleep(0.15)

                    elif data.get("type") == "reset":
                        self.reset_memory()
                        logging.info("Memory wiped due to simulation reset.")

        except Exception as e:
            logging.error(f"Connection error: {e}")

    async def deliberate(self):
        """Routes the deliberation based on the presence of a target (Maze vs Room)."""
        if self.current_state.get("target") is not None:
            return await self.deliberate_maze()
        else:
            return await self.deliberate_room()

    async def deliberate_maze(self):
        raise NotImplementedError("Subclasses must implement deliberate_maze()")

    async def deliberate_room(self):
        raise NotImplementedError("Subclasses must implement deliberate_room()")

    def reset_memory(self):
        """Clears internal tracking variables when the simulation resets."""
        pass

    async def send_telemetry(self, websocket):
        """Packages internal memory/probabilities and sends them to the frontend UI."""
        pass
