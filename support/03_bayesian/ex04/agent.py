import numpy as np

class FlappyAgent:
    def __init__(self):
        self.knowledge = {}

    def get_probs(self, state_key):
        if state_key not in self.knowledge:
            # Neutral prior
            self.knowledge[state_key] = [0.5, 0.5]
        return np.array(self.knowledge[state_key])

    def get_state_key(self, by, py_b):
        # YOUR EXACT RULE LOGIC: Target is 48px above the bottom pipe
        target_y = py_b - 48
        
        # Distance to your target line
        dist_v = by - target_y

        # Compress into 10-pixel bins. 
        # State space is tiny! Just d-5 to d5.
        d_bin = int(np.clip(dist_v // 10, -5, 5))

        return f"d{d_bin}"

    def update(self, history, final_score, lr):
        for state_key, action_idx, dist_to_gap in history:
            probs = self.get_probs(state_key)

            try:
                d_bin = int(state_key.replace("d", ""))
            except Exception:
                continue 

            target_prob = probs[action_idx] 
            weight = 0.0

            # THE 1D SHAPED REWARD
            if action_idx == 1: # CLICK
                if d_bin < 0: 
                    # Above your target line: Do not click!
                    target_prob = 0.0
                    weight = 1.0  
                elif d_bin >= 0: 
                    # Below your target line: Click!
                    target_prob = 1.0
                    weight = 0.8  
                    
            else: # IDLE
                if d_bin >= 0: 
                    # Below your target line: Do not idle!
                    target_prob = 0.0
                    weight = 1.0  
                elif d_bin < 0:
                    # Above your target line: Safe to fall.
                    target_prob = 1.0
                    weight = 0.8  

            if weight > 0:
                probs[action_idx] += lr * weight * (target_prob - probs[action_idx])
                probs = np.clip(probs, 0.01, 0.99)
                self.knowledge[state_key] = (probs / np.sum(probs)).tolist()

    def decide(self, by, py_b, temp=0.1, deterministic=False):
        state_key = self.get_state_key(by, py_b)
        probs = self.get_probs(state_key)

        if deterministic:
            return "CLICK" if np.argmax(probs) == 1 else "IDLE"

        logits = np.log(probs + 1e-10)
        exp_logits = np.exp(logits / temp)
        softmax_probs = exp_logits / np.sum(exp_logits)

        return np.random.choice(["IDLE", "CLICK"], p=softmax_probs)

    def save(self, path):
        import json

        with open(path, "w") as f:
            json.dump(self.knowledge, f)

    def load(self, path):
        import json
        import os

        if os.path.exists(path):
            with open(path, "r") as f:
                self.knowledge = json.load(f)
