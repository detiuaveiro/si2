import argparse
import asyncio
import json
import uuid

import websockets
from tqdm import tqdm

from .agent import FlappyAgent


async def run_episode(url, agent, args, is_train=True, epoch=0):
    identification = str(uuid.uuid4())[:8]
    history = []

    # Calculate Decayed Hyperparameters
    current_lr = args.learning_rate / (1.0 + 0.0001 * epoch) if is_train else 0
    current_temp = max(0.01, args.temp * (0.999**epoch)) if is_train else 0.01

    async with websockets.connect(f"{url}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "id": identification}))

        async for message in websocket:
            data = json.loads(message)

            if data["evt"] == "world_state":
                player = data["players"].get(identification)
                if not player:
                    continue

                closest_pipe = data["pipes"][0]
                for pipe in data["pipes"]:
                    if pipe["px"] + 60 > player["px"]:
                        closest_pipe = pipe
                        break

                # 2. State Calculation
                pc = closest_pipe["py_b"]
                by = player["py"]

                state_key = agent.get_state_key(by, pc)

                # 3. Decision
                action = agent.decide(
                    by, pc, temp=current_temp, deterministic=not is_train
                )

                print(f"{state_key:<10} {action:<5}")

                if action == "CLICK":
                    await websocket.send(json.dumps({"cmd": "click"}))

                if is_train:
                    dist_to_gap = by - pc

                    # Store history to process at the end of the episode
                    history.append(
                        (state_key, 1 if action == "CLICK" else 0, dist_to_gap)
                    )

            elif data["evt"] == "done":
                final_score = data["highscore"]
                if is_train:
                    # Trigger the shaped Bayesian update
                    agent.update(history, final_score, current_lr)
                return final_score


def main():
    parser = argparse.ArgumentParser(description="Bayesian Flappy Bird Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True)
    parser.add_argument("-u", "--url", default="ws://localhost:8765")

    train_group = parser.add_argument_group("Training Options")
    train_group.add_argument("-e", "--epochs", type=int, default=1000)
    train_group.add_argument("-lr", "--learning-rate", type=float, default=0.5)
    train_group.add_argument("-t", "--temp", type=float, default=1.0)
    train_group.add_argument("-o", "--output", default="flappy_model.json")

    play_group = parser.add_argument_group("Play Options")
    play_group.add_argument("-i", "--input", default="flappy_model.json")

    args = parser.parse_args()
    agent = FlappyAgent()

    if args.mode == "train":
        for e in tqdm(range(args.epochs)):
            asyncio.run(run_episode(args.url, agent, args, is_train=True, epoch=e))
        agent.save(args.output)
    else:
        agent.load(args.input)
        score = asyncio.run(run_episode(args.url, agent, args, is_train=False))
        print(f"Final Play Score: {score}")


if __name__ == "__main__":
    main()
