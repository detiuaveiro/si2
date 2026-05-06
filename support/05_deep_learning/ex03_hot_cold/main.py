import argparse
import os
import sys
import numpy as np
from tqdm import tqdm

# Suppress informational logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# Set backend to JAX
os.environ["KERAS_BACKEND"] = "jax"
import keras

class TQDMCallback(keras.callbacks.Callback):
    def on_train_begin(self, logs=None):
        self.pbar = tqdm(total=self.params['epochs'], desc="Training", unit="epoch")
    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs: self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})
    def on_train_end(self, logs=None):
        self.pbar.close()

def get_augmented_state(low, high):
    """
    Returns a 4D state: [normalized_low, normalized_high, normalized_mid, normalized_range]
    Providing the midpoint and range size helps the NN learn the bisection logic.
    """
    low_f = low / 100.0
    high_f = high / 100.0
    mid_f = (low_f + high_f) / 2.0
    range_f = (high - low) / 100.0
    return [low_f, high_f, mid_f, range_f]

def generate(num_samples=50000):
    states, actions = [], []
    print(f"Generating {num_samples} samples from binary search expert...")
    for _ in tqdm(range(num_samples), desc="Simulating"):
        low, high = 1, 100
        secret = np.random.randint(1, 101)
        curr_low, curr_high = low, high
        # Ensure we cover the full range of possible bisections
        while curr_low <= curr_high:
            guess = (curr_low + curr_high) // 2
            states.append(get_augmented_state(curr_low, curr_high))
            actions.append(guess / 100.0)
            if guess == secret: break
            elif guess < secret: curr_low = guess + 1
            else: curr_high = guess - 1
            if len(states) >= num_samples: break
        if len(states) >= num_samples: break
                
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    np.save(os.path.join(data_dir, "X.npy"), np.array(states))
    np.save(os.path.join(data_dir, "y.npy"), np.array(actions))

def train(epochs=50, batch_size=64, force_gen=False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    x_path = os.path.join(data_dir, "X.npy")
    
    if force_gen or not os.path.exists(x_path):
        generate()
        
    X = np.load(x_path)
    y = np.load(os.path.join(data_dir, "y.npy"))
    
    # Deeper model for more precise regression
    model = keras.Sequential([
        keras.layers.Input(shape=(4,)),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(128, activation="relu"),
        keras.layers.Dense(64, activation="relu"),
        keras.layers.Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    
    print(f"Training model for {epochs} epochs...")
    model.fit(X, y, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=0, callbacks=[TQDMCallback()])
    
    model_path = os.path.join(base_dir, "model.keras")
    model.save(model_path)
    print(f"Model saved to {model_path}")

def play(secret_num=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "model.keras")
    if not os.path.exists(model_path):
        print(f"Error: Model not found. Run --mode train first.")
        return False
        
    model = keras.models.load_model(model_path)
    if secret_num is None:
        secret_num = np.random.randint(1, 101)
    print(f"Secret number is: {secret_num}")
    
    curr_low, curr_high = 1, 100
    for i in range(1, 15): # Give it slightly more turns for precision safety
        state = np.array([get_augmented_state(curr_low, curr_high)])
        prediction = model.predict(state, verbose=0)[0][0]
        guess = int(round(prediction * 100))
        guess = max(curr_low, min(curr_high, guess))
        
        print(f"Turn {i}: Agent guesses {guess} (Predicted {prediction*100:.2f})")
        if guess == secret_num:
            print(f"Correct! Agent won in {i} turns.")
            return True
        elif guess < secret_num:
            print("Feedback: Higher")
            curr_low = guess + 1
        else:
            print("Feedback: Lower")
            curr_high = guess - 1
            
        if curr_low > curr_high:
            print("Agent narrowed it down but missed. Range exhausted.")
            break
            
    print("Agent failed.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Deep Learning - Hot/Cold Agent")
    parser.add_argument("-m", "--mode", choices=["train", "play"], required=True, 
                        help="Mode to run: train or play")
    
    train_group = parser.add_argument_group("Training Options")
    train_group.add_argument("-e", "--epochs", type=int, default=50, help="Number of training epochs")
    train_group.add_argument("-b", "--batch-size", type=int, default=64, help="Batch size for training")
    train_group.add_argument("-f", "--force-generate", action="store_true", help="Force dataset regeneration")
    
    play_group = parser.add_argument_group("Playing Options")
    play_group.add_argument("-s", "--secret", type=int, default=None, help="Secret number for playing (1-100)")
    
    args = parser.parse_args()

    if args.mode == "train":
        train(args.epochs, args.batch_size, args.force_generate)
    elif args.mode == "play":
        play(args.secret)

if __name__ == "__main__":
    main()
