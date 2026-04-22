import argparse
import logging
import random
import sys

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures


def setup_logger(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stdout)
    return logging.getLogger("MLAgent")


class MLGuesser:
    def __init__(self, lower, upper, dynamic_bounds=True):
        self.original_lower = lower
        self.original_upper = upper

        self.current_lower = lower
        self.current_upper = upper
        self.last_guess = None
        self.last_hint = None

        self.dynamic_bounds = dynamic_bounds

        # THE FIX: Wrap Linear Regression in a Polynomial pipeline.
        # This creates interaction terms (like guess * hint) so the
        # linear model can handle the conditional branching.
        self.model = make_pipeline(PolynomialFeatures(degree=2, include_bias=False), LinearRegression())
        self._pretrain_on_synthetic_data()

    def _pretrain_on_synthetic_data(self, samples=20000):
        logging.debug("Pre-training Polynomial-Linear model on synthetic data...")
        X = []
        y = []

        for _ in range(samples):
            sim_min = random.randint(0, 500)
            sim_max = random.randint(sim_min + 10, sim_min + 1000)

            sim_guess = random.randint(sim_min, sim_max)
            sim_secret = random.randint(sim_min, sim_max)

            if sim_guess == sim_secret:
                continue

            hint_str = "hot" if sim_guess > sim_secret else "cold"
            hint_encoded = 1 if hint_str == "hot" else -1

            if hint_str == "hot":
                new_max = sim_guess - 1
                ideal_guess = (sim_min + new_max) // 2
            else:
                new_min = sim_guess + 1
                ideal_guess = (new_min + sim_max) // 2

            X.append([sim_min, sim_max, sim_guess, hint_encoded])
            y.append(ideal_guess)

        self.model.fit(X, y)
        logging.debug("Pre-training complete.")

    def update(self, guess, hint):
        self.last_guess = guess
        self.last_hint = hint

        if self.dynamic_bounds:
            if hint == "hot":
                self.current_upper = min(self.current_upper, guess - 1)
            elif hint == "cold":
                self.current_lower = max(self.current_lower, guess + 1)

        logging.debug(f"Current internal bounds: [{self.current_lower}, {self.current_upper}]")

    def make_decision(self):
        if self.last_guess is None:
            return random.randint(self.original_lower, self.original_upper)

        hint_encoded = 1 if self.last_hint == "hot" else -1

        b_min = self.current_lower if self.dynamic_bounds else self.original_lower
        b_max = self.current_upper if self.dynamic_bounds else self.original_upper

        state_X = np.array([[b_min, b_max, self.last_guess, hint_encoded]])
        pred_guess = self.model.predict(state_X)[0]

        clamped_guess = int(np.clip(round(pred_guess), self.current_lower, self.current_upper))

        # Anti-Stagnation Fix (still needed for integer rounding limits)
        if clamped_guess == self.last_guess:
            if self.last_hint == "hot":
                clamped_guess -= 1
            elif self.last_hint == "cold":
                clamped_guess += 1

        clamped_guess = int(np.clip(clamped_guess, self.current_lower, self.current_upper))
        return clamped_guess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lower", type=int, default=1)
    parser.add_argument("-u", "--upper", type=int, default=100)
    parser.add_argument("-s", "--secret", type=int, required=True)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--dynamic", action="store_true", help="Enable dynamic boundary updating")
    args = parser.parse_args()

    logger = setup_logger(args.verbose)
    agent = MLGuesser(args.lower, args.upper, dynamic_bounds=args.dynamic)

    guess = random.randint(args.lower, args.upper)

    logger.info("--- New Polynomial-Linear ML Game ---")
    logger.info(f"Range: [{args.lower}, {args.upper}] | Secret: {args.secret} | Dynamic Bounds: {args.dynamic}\n")

    for i in range(1, 20):
        if guess == args.secret:
            logger.info(f"Step {i}: Guess {guess} -> Found!")
            break

        hint = "hot" if guess > args.secret else "cold"
        logger.info(f"Step {i}: Guess {guess} -> Hint: {hint}")

        agent.update(guess, hint)
        guess = agent.make_decision()

    else:
        logger.info(f"Failed to find the secret ({args.secret}) within the attempt limit.")


if __name__ == "__main__":
    main()
