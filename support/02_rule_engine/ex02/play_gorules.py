import argparse
import asyncio
import json
import logging
import uuid

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
wslogger = logging.getLogger("websockets")
wslogger.setLevel(logging.WARN)

# --- CONFIGURATION: Students update these ---
PROJECT_ID = "YOUR_PROJECT_ID_HERE"
DOCUMENT_PATH = "flappy_rules"
GORULES_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

GORULES_URL = (
    f"http://localhost:8080/api/projects/{PROJECT_ID}/evaluate/{DOCUMENT_PATH}"
)
HEADERS = {"Content-Type": "application/json", "X-Access-Token": GORULES_TOKEN}
# ------------------------------------------


async def player_game(url: str) -> float:
    """
    Player main loop using GoRules BRMS API for decision making.
    """
    identification = str(uuid.uuid4())[:8]
    final_score = 0.0

    async with websockets.connect(f"{url}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "id": identification}))
        done = False

        while not done:
            data = json.loads(await websocket.recv())

            if data["evt"] == "world_state":
                player = data["players"].get(identification)
                if not player:
                    continue

                # Find closest pipe
                closest_pipe = data["pipes"][0]
                for pipe in data["pipes"]:
                    if pipe["px"] + 60 > player["px"]:
                        closest_pipe = pipe
                        break

                # Calculate variables for GoRules
                # The gap center is exactly halfway between the top and bottom pipe pieces
                c = (closest_pipe["py_t"] + closest_pipe["py_b"]) / 2.0
                py = player["py"]

                # 1. Prepare the JSON payload context for GoRules
                payload = {"context": {"bird_y": py, "next_pipe_center_y": c}}

                try:
                    # 2. Query the GoRules REST API (Timeout set low to maintain framerate)
                    # We use asyncio.to_thread so the blocking requests.post doesn't crash the websocket
                    response = await asyncio.to_thread(
                        requests.post,
                        GORULES_URL,
                        json=payload,
                        headers=HEADERS,
                        timeout=0.1,
                    )

                    if response.status_code == 200:
                        result_data = response.json().get("result", {})

                        # 3. If GoRules deduced 'jump', send the click command
                        if result_data.get("action") == "jump":
                            await websocket.send(json.dumps({"cmd": "click"}))
                    else:
                        logger.error(
                            f"API Error: {response.status_code} - {response.text}"
                        )

                except requests.exceptions.RequestException as e:
                    logger.warning(
                        f"Failed to reach GoRules API (it might be too slow): {e}"
                    )

            elif data["evt"] == "done":
                done = True
                final_score = data["highscore"]

    return final_score


def main(args: argparse.Namespace) -> None:
    highscore = asyncio.run(player_game(args.u))
    logger.info(f"Highscore: {highscore}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Play the game using GoRules BRMS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-u", type=str, help="server url", default="ws://localhost:8765"
    )
    args = parser.parse_args()
    main(args)
