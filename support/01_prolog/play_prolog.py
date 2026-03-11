#!/usr/bin/env python

import argparse
import asyncio
import json
import logging
import uuid

import websockets
from pyswip import Prolog

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
wslogger = logging.getLogger("websockets")
wslogger.setLevel(logging.WARN)


async def player_game(url: str, prolog_file: str) -> float:
    """
    Player main loop using Prolog for decision making.
    """
    # Initialize Prolog and load our rules
    prolog = Prolog()
    prolog.consult(prolog_file)

    identification = str(uuid.uuid4())[:8]
    final_score = 0.0

    async with websockets.connect(f"{url}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "id": identification}))
        done = False

        while not done:
            data = json.loads(await websocket.recv())

            if data["evt"] == "world_state":
                player = data["players"][identification]

                # Find closest pipe
                closest_pipe = data["pipes"][0]
                for pipe in data["pipes"]:
                    if pipe["px"] + 60 > player["px"]:
                        closest_pipe = pipe
                        break

                # Calculate variables for Prolog
                # The gap center is exactly halfway between the top and bottom pipe pieces
                c = (closest_pipe["py_t"] + closest_pipe["py_b"]) / 2.0
                py = player["py"]
                v = player["v"]
                px = closest_pipe["px"]

                # 1. Query the Prolog entry point
                # pyswip returns a generator of dictionaries with the unified variables
                query = f"step({py}, {v}, {c}, {px}, Action)"
                result = list(prolog.query(query))

                # If Prolog deduced 'jump', send the click command
                if result and result[0]["Action"] == "jump":
                    await websocket.send(json.dumps({"cmd": "click"}))

            elif data["evt"] == "done":
                done = True
                final_score = data["highscore"]

    return final_score


def main(args: argparse.Namespace) -> None:
    highscore = asyncio.run(player_game(args.u, args.p))
    logger.info(f"Highscore: {highscore}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Play the game using Prolog",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-u", type=str, help="server url", default="ws://localhost:8765"
    )
    parser.add_argument(
        "-p", type=str, help="Prolog file to load (e.g., bot.pl)", required=True
    )
    args = parser.parse_args()
    main(args)
