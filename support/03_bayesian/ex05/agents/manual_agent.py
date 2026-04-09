import asyncio
import json
import sys
import tty
import termios
from base_agent import BaseAgent

def getch():
    """Reads a single character from the standard input (Linux/macOS)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch.lower()

class ManualAgent(BaseAgent):
    """
    An agent controlled manually via the terminal using W, A, S, D keys instantly.
    """

    def __init__(self, server_uri="ws://localhost:8765"):
        super().__init__(server_uri)
        self.key_mapping = {'w': 'N', 's': 'S', 'd': 'E', 'a': 'W'}

    async def get_manual_action(self):
        """Prompts the user for a valid WASD input."""
        
        if self.current_state.get("objective_reached"):
            return None

        valid_actions = self.current_state.get("valid_actions", [])
        
        print(f"\n--- Agent at {self.current_state.get('position')} ---")
        print(f"Valid directions: {valid_actions}")
        print("Press W/A/S/D to move... ", end="", flush=True)
        
        while True:
            # Run the blocking terminal read in a background thread
            user_input = await asyncio.to_thread(getch)

            # Catch Ctrl+C (ASCII character 3) for clean exits in raw mode
            if user_input == '\x03':
                print("\nExiting...")
                sys.exit(0)

            if user_input in self.key_mapping:
                action = self.key_mapping[user_input]
                
                if action in valid_actions:
                    print(action) 
                    return action
                else:
                    print(f"\rObstacle at {action}. Try again (W/A/S/D)... ", end="", flush=True)

    async def deliberate_maze(self):
        return await self.get_manual_action()

    async def deliberate_room(self):
        return await self.get_manual_action()

    async def send_telemetry(self, websocket):
        """Send blank telemetry to satisfy the UI requirement."""
        payload = {
            "action": "telemetry",
            "data": {
                "visited": [],
                "current_probs": {"N": 0.0, "S": 0.0, "E": 0.0, "W": 0.0}
            }
        }
        await websocket.send(json.dumps(payload))

if __name__ == "__main__":
    agent = ManualAgent()
    print("Starting Manual Agent...")
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\nAgent shut down manually.")
