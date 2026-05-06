import os, argparse, numpy as np, matplotlib.pyplot as plt
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "jax"
import keras

class TQDMProgressBar(keras.callbacks.Callback):
    def on_train_begin(self, logs=None): self.pbar = tqdm(total=self.params['epochs'], desc="Training", unit="epoch")
    def on_epoch_end(self, epoch, logs=None):
        self.pbar.update(1)
        if logs: self.pbar.set_postfix({k: f"{v:.4f}" for k, v in logs.items()})
    def on_train_end(self, logs=None): self.pbar.close()

def load_mnist():
    (x_tr, y_tr), (x_te, y_te) = keras.datasets.mnist.load_data()
    x_tr, x_te = x_tr.astype("float32")/255.0, x_te.astype("float32")/255.0
    x_tr, x_te = np.expand_dims(x_tr, -1), np.expand_dims(x_te, -1)
    y_te_orig = y_te.copy()
    y_tr, y_te = keras.utils.to_categorical(y_tr, 10), keras.utils.to_categorical(y_te, 10)
    return x_tr, y_tr, x_te, y_te, y_te_orig

def build_cnn():
    model = keras.Sequential([keras.layers.Input(shape=(28,28,1)), keras.layers.Conv2D(32, 3, activation="relu"), keras.layers.MaxPooling2D(2), keras.layers.Conv2D(64, 3, activation="relu"), keras.layers.MaxPooling2D(2), keras.layers.Flatten(), keras.layers.Dropout(0.5), keras.layers.Dense(10, activation="softmax")])
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
    return model

def plot_samples(x, y):
    plt.figure(figsize=(8,8))
    for i in range(9): plt.subplot(3,3,i+1); plt.imshow(x[i].reshape(28,28), cmap='gray'); plt.title(f"L: {np.argmax(y[i])}"); plt.axis('off')
    plt.show()

class InteractivePredictor:
    def __init__(self, model):
        self.model = model; self.f_model = keras.Model(inputs=model.inputs, outputs=model.layers[0].output)
        self.grid = np.zeros((28, 28)); self.fig, self.ax = plt.subplots(1, 3, figsize=(15, 5))
        self.drawing = False
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.update_ui(); plt.show()
    def on_press(self, e): 
        if e.inaxes == self.ax[0]: self.drawing = True; self.paint(e)
    def on_release(self, e): self.drawing = False; self.predict()
    def on_motion(self, e):
        if self.drawing and e.inaxes == self.ax[0]: self.paint(e)
    def on_key(self, e):
        if e.key == 'c': self.grid.fill(0); self.update_ui()
        elif e.key == 'q': plt.close()
    def paint(self, e):
        if e.xdata is None or e.ydata is None: return
        ix, iy = int(round(e.xdata)), int(round(e.ydata))
        for dx in range(-1,2):
            for dy in range(-1,2):
                if 0<=ix+dx<28 and 0<=iy+dy<28: self.grid[iy+dy, ix+dx] = 1.0
        self.update_ui()
    def update_ui(self):
        self.ax[0].clear(); self.ax[0].imshow(self.grid, cmap='gray', vmin=0, vmax=1); self.ax[0].axis('off'); self.fig.canvas.draw_idle()
    def predict(self):
        inp = self.grid.reshape(1,28,28,1); p = self.model.predict(inp, verbose=0)[0]; f = self.f_model.predict(inp, verbose=0)[0]
        self.ax[1].clear(); self.ax[1].imshow(f[:,:,0], cmap='viridis'); self.ax[1].axis('off')
        self.ax[2].clear(); self.ax[2].bar(range(10), p); self.ax[2].set_title(f"Pred: {np.argmax(p)}"); self.fig.canvas.draw_idle()

def main():
    parser = argparse.ArgumentParser(description="CNN MNIST Example")
    train_group = parser.add_argument_group("Training Options")
    train_group.add_argument("-e", "--epochs", type=int, default=20); train_group.add_argument("-b", "--batch-size", type=int, default=64); train_group.add_argument("-s", "--subset", type=int, default=20000)
    play_group = parser.add_argument_group("Playing Options")
    play_group.add_argument("-i", "--interactive", action="store_true")
    args = parser.parse_args()
    x_tr, y_tr, x_te, y_te, y_te_orig = load_mnist()
    if not args.interactive: plot_samples(x_tr, y_tr)
    model = build_cnn()
    history = model.fit(x_tr[:args.subset], y_tr[:args.subset], batch_size=args.batch_size, epochs=args.epochs, validation_split=0.1, verbose=0, callbacks=[keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True), TQDMProgressBar()])
    if args.interactive: InteractivePredictor(model)
    else: print(f"Acc: {model.evaluate(x_te[:1000], y_te[:1000], verbose=0)[1]:.4f}")

if __name__ == "__main__": main()
