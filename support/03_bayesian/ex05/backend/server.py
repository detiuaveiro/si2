import asyncio
import json
import logging
import os

# Configure standard logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SimulationServer:
    def __init__(self):
        self.frontend_ws = None
        self.agent_ws = None
        self.maps_dir = "maps"
        self.current_map = None
        self.sim_state = {}
        self.running = False

        if not os.path.exists(self.maps_dir):
            os.makedirs(self.maps_dir)
            logging.info(f"Created maps directory at: {os.path.abspath(self.maps_dir)}")

    async def start(self, host="0.0.0.0", port=8765):
        import websockets

        logging.info(f"Starting websocket server on ws://{host}:{port}")
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()

    async def handle_client(self, websocket):
        client_type = "Unknown"
        try:
            init_msg = await websocket.recv()
            data = json.loads(init_msg)
            client_type = data.get("client", "Unknown")

            if client_type == "frontend":
                logging.info("Frontend connected.")
                self.frontend_ws = websocket
                await self.send_map_list()
                await self.frontend_loop(websocket)
            elif client_type == "agent":
                logging.info("Agent connected.")
                self.agent_ws = websocket
                if self.running:
                    await self.send_agent_state()
                await self.agent_loop(websocket)
            else:
                logging.warning(
                    f"Unknown client type attempted connection: {client_type}"
                )

        except websockets.exceptions.ConnectionClosed:
            logging.info(f"{client_type} disconnected cleanly.")
        except Exception as e:
            logging.error(f"Error handling client {client_type}: {e}")
        finally:
            if websocket == self.frontend_ws:
                self.frontend_ws = None
                logging.info("Frontend session cleared.")
            elif websocket == self.agent_ws:
                self.agent_ws = None
                logging.info("Agent session cleared.")

    async def frontend_loop(self, websocket):
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")

                if action == "load_map":
                    self.load_map(data.get("filename"))
                    await self.update_frontend()
                    if self.agent_ws:
                        await self.agent_ws.send(json.dumps({"type": "reset"}))
                        await self.send_agent_state()
                elif action == "save_map":
                    self.save_map(data.get("filename"), data.get("map_data"))
                    await self.send_map_list()
                elif action == "start_sim":
                    self.running = True
                    logging.info("Simulation started via frontend.")
                    await self.update_frontend()
                    if self.agent_ws:
                        await self.send_agent_state()
                elif action == "stop_sim":
                    self.running = False
                    logging.info("Simulation stopped via frontend.")
                    await self.update_frontend()
                elif action == "reset_sim":
                    self.reset_sim()
                    await self.update_frontend()
                    if self.agent_ws:
                        await self.agent_ws.send(json.dumps({"type": "reset"}))
                        await self.send_agent_state()
            except Exception as e:
                logging.error(f"Error processing frontend message: {e}")

    async def agent_loop(self, websocket):
        async for message in websocket:
            if not self.running or not self.current_map:
                continue
            try:
                data = json.loads(message)
                if data.get("action") == "move":
                    direction = data.get("direction")
                    self.process_move(direction)
                    self.check_objective()
                    await self.update_frontend()
                    await self.send_agent_state()
                elif data.get("action") == "telemetry":
                    if self.frontend_ws:
                        await self.frontend_ws.send(
                            json.dumps(
                                {"type": "agent_telemetry", "data": data.get("data")}
                            )
                        )
            except Exception as e:
                logging.error(f"Error processing agent message: {e}")

    def process_move(self, direction):
        x, y = self.sim_state["agent_pos"]
        nx, ny = x, y

        if direction == "N":
            ny -= 1
        elif direction == "S":
            ny += 1
        elif direction == "E":
            nx += 1
        elif direction == "W":
            nx -= 1

        width = self.current_map["width"]
        height = self.current_map["height"]

        if 0 <= nx < width and 0 <= ny < height:
            cell = self.current_map["grid"][ny][nx]
            if cell == "obstacle":
                key = f"{nx},{ny}"
                self.sim_state["hits"][key] = self.sim_state["hits"].get(key, 0) + 1
                logging.debug(f"Agent hit obstacle at {nx},{ny}")
            else:
                self.sim_state["agent_pos"] = [nx, ny]
                key = f"{nx},{ny}"
                self.sim_state["visits"][key] = self.sim_state["visits"].get(key, 0) + 1
                logging.debug(f"Agent moved to {nx},{ny}")

    def reset_sim(self):
        """Resets the map state and heatmaps to their initial conditions."""
        if self.current_map:
            start_pos = self.current_map.get("start", [0, 0])
            self.sim_state = {
                "agent_pos": start_pos,
                "visits": {f"{start_pos[0]},{start_pos[1]}": 1},
                "hits": {},
            }
            self.running = False
            logging.info("Simulation reset to start state.")

    def check_objective(self):
        if self.current_map["type"] == "maze":
            if self.sim_state["agent_pos"] == self.current_map.get("target"):
                self.running = False
                logging.info("Objective Reached: Maze target found!")
        elif self.current_map["type"] == "room":
            total_floor = sum(
                1
                for row in self.current_map["grid"]
                for cell in row
                if cell != "obstacle"
            )
            if len(self.sim_state["visits"]) >= total_floor:
                self.running = False
                logging.info("Objective Reached: Room fully explored!")

    def get_valid_actions(self):
        x, y = self.sim_state["agent_pos"]
        width = self.current_map["width"]
        height = self.current_map["height"]
        actions = []

        if y > 0 and self.current_map["grid"][y - 1][x] != "obstacle":
            actions.append("N")
        if y < height - 1 and self.current_map["grid"][y + 1][x] != "obstacle":
            actions.append("S")
        if x < width - 1 and self.current_map["grid"][y][x + 1] != "obstacle":
            actions.append("E")
        if x > 0 and self.current_map["grid"][y][x - 1] != "obstacle":
            actions.append("W")
        return actions

    async def send_agent_state(self):
        if self.agent_ws:
            payload = {
                "type": "state",
                "position": self.sim_state["agent_pos"],
                "valid_actions": self.get_valid_actions(),
                "objective_reached": not self.running,
                "target": self.current_map.get("target")
                if self.current_map["type"] == "maze"
                else None,
                "start": self.current_map.get("start"),
                "width": self.current_map.get("width"),
                "height": self.current_map.get("height"),
            }
            await self.agent_ws.send(json.dumps(payload))

    async def update_frontend(self):
        if self.frontend_ws:
            payload = {
                "type": "update",
                "map": self.current_map,
                "state": self.sim_state,
                "running": self.running,
                "agent_connected": self.agent_ws is not None,
            }
            await self.frontend_ws.send(json.dumps(payload))

    async def send_map_list(self):
        if self.frontend_ws:
            try:
                maps = sorted(
                    [f for f in os.listdir(self.maps_dir) if f.endswith(".json")]
                )
                await self.frontend_ws.send(
                    json.dumps({"type": "map_list", "maps": maps})
                )
            except Exception as e:
                logging.error(f"Failed to read maps directory: {e}")

    def load_map(self, filename):
        try:
            filepath = os.path.join(self.maps_dir, filename)
            with open(filepath, "r") as f:
                self.current_map = json.load(f)

            start_pos = self.current_map.get("start", [0, 0])
            self.sim_state = {
                "agent_pos": start_pos,
                "visits": {f"{start_pos[0]},{start_pos[1]}": 1},
                "hits": {},
            }
            self.running = False
            logging.info(f"Successfully loaded map: {filename}")
        except Exception as e:
            logging.error(f"Failed to load map {filename}: {e}")

    def save_map(self, filename, map_data):
        try:
            if not filename.endswith(".json"):
                filename += ".json"
            filepath = os.path.join(self.maps_dir, filename)

            with open(filepath, "w") as f:
                json.dump(map_data, f)
            logging.info(f"Successfully saved map: {filepath}")
        except PermissionError:
            logging.error(
                f"Permission denied when saving {filename}. Check Docker volume permissions."
            )
        except Exception as e:
            logging.error(f"Unexpected error saving map {filename}: {e}")


if __name__ == "__main__":
    server = SimulationServer()
    asyncio.run(server.start())
