import os, argparse, numpy as np, matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

class TQDMProgressBar(keras.callbacks.Callback):
    def on_train_begin(self, logs=None): self.pbar = tqdm(total=self.params['epochs'], desc="Training", unit="epoch")
    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs: self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})
    def on_train_end(self, logs=None): self.pbar.close()

def generate_data(n=1200):
    X = np.random.randn(n, 2)
    y = (np.sum(X**2, axis=1) < 1).astype(int)
    return X, y

def build_model():
    model = keras.Sequential([keras.layers.Input(shape=(2,)), keras.layers.Dense(32, activation="relu"), keras.layers.Dense(32, activation="relu"), keras.layers.Dense(1, activation="sigmoid")])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

def plot_history(history):
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1); plt.plot(history.history['loss'], label='Train Loss')
    if 'val_loss' in history.history: plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Loss History'); plt.legend()
    plt.subplot(1, 2, 2); plt.plot(history.history['accuracy'], label='Train Acc')
    if 'val_accuracy' in history.history: plt.plot(history.history['val_accuracy'], label='Val Acc')
    plt.title('Accuracy History'); plt.legend(); plt.show()

def plot_cm(y_true, y_pred):
    cm = confusion_matrix(y_true, (y_pred > 0.5).astype(int))
    fig, ax = plt.subplots(figsize=(6, 6))
    ConfusionMatrixDisplay(confusion_matrix=cm).plot(cmap=plt.cm.Blues, ax=ax)
    ax.set_title('Confusion Matrix'); plt.show()

def plot_data(X, y):
    plt.figure(figsize=(8, 6)); plt.scatter(X[y==0,0], X[y==0,1], c='blue', alpha=0.6, label='C0')
    plt.scatter(X[y==1,0], X[y==1,1], c='red', alpha=0.6, label='C1')
    plt.title('Dataset'); plt.legend(); plt.show()

def plot_decision_boundary(model, X, y):
    x_min, x_max = X[:,0].min()-0.5, X[:,0].max()+0.5
    y_min, y_max = X[:,1].min()-0.5, X[:,1].max()+0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1), np.arange(y_min, y_max, 0.1))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()], verbose=0).reshape(xx.shape)
    plt.figure(figsize=(10, 8)); plt.contourf(xx, yy, Z, cmap=plt.cm.RdBu, alpha=0.8)
    plt.scatter(X[:,0], X[:,1], c=y, cmap=plt.cm.RdBu, edgecolors='w'); plt.show()

def main():
    parser = argparse.ArgumentParser(description="Foundational MLP Example")
    train_group = parser.add_argument_group("Training Options")
    train_group.add_argument("-e", "--epochs", type=int, default=100)
    train_group.add_argument("-b", "--batch-size", type=int, default=32)
    args = parser.parse_args()
    X, y = generate_data()
    plot_data(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = build_model()
    history = model.fit(X_train, y_train, epochs=args.epochs, batch_size=args.batch_size, validation_split=0.1, verbose=0, callbacks=[keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True), TQDMProgressBar()])
    print(f"Final Accuracy: {model.evaluate(X_test, y_test, verbose=0)[1]:.4f}")
    plot_history(history); plot_cm(y_test, model.predict(X_test, verbose=0)); plot_decision_boundary(model, X_test, y_test)

if __name__ == "__main__": main()
