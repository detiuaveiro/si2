import argparse
import logging
import random
import sys

import numpy as np

def setup_logger(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stdout)
    return logging.getLogger("BayesianAgent")


class ImprovedBayesianGuesser:
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
        self.size = upper - lower + 1
        self.numbers = np.arange(lower, upper + 1)
        self.beliefs = np.full(self.size, 1.0 / self.size)

    def update(self, guess, hint):
        idx = guess - self.lower

        # Rules:
        # Hot = Too High (Secret is lower) -> Remove everything >= guess
        # Cold = Too Low (Secret is higher) -> Remove everything <= guess
        if hint == "hot":
            self.beliefs[idx:] = 0
        elif hint == "cold":
            self.beliefs[: idx + 1] = 0

        total = np.sum(self.beliefs)
        if total > 0:
            self.beliefs /= total
        else:
            # This only triggers if the 'Hint' contradicts previous knowledge
            logging.debug("❌ Logic Error: Belief set collapsed.")

        # Single debug print per update
        readable = {
            int(n): round(float(b), 3)
            for n, b in zip(self.numbers, self.beliefs)
            if b > 0
        }
        logging.debug(f"Possible Numbers: {readable}")

    def make_decision(self):
        # Fallback if logic collapses, pick randomly from what was originally possible
        if np.sum(self.beliefs) == 0:
            return random.randint(self.lower, self.upper)

        # Stochastic choice based on current probability weights
        return int(random.choices(self.numbers, weights=self.beliefs.tolist(), k=1)[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lower", type=int, default=1)
    parser.add_argument("-u", "--upper", type=int, default=10)
    parser.add_argument("-s", "--secret", type=int, required=True)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    logger = setup_logger(args.verbose)

    agent = ImprovedBayesianGuesser(args.lower, args.upper)

    # Start with a random guess
    guess = random.randint(args.lower, args.upper)

    logger.info(
        f"--- New Game ---\nRange: [{args.lower}, {args.upper}] | Secret: {args.secret}\n"
    )

    for i in range(1, 20):  # Reasonable attempt limit
        if guess == args.secret:
            logger.info(f"Step {i}: Guess {guess} -> Found!")
            break

        hint = "hot" if guess > args.secret else "cold"
        logger.info(f"Step {i}: Guess {guess} -> Hint: {hint}")

        # 1. Update the knowledge base based on the hint
        agent.update(guess, hint)

        # 2. Pick the NEXT guess based on the new knowledge
        guess = agent.make_decision()

        # 2. Pick the NEXT guess based on the new knowledge
        guess = agent.make_decision()

if __name__ == "__main__":
    main()
