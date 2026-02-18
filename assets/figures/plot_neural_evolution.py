import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks


def plot_activation_functions():
    z = np.linspace(-5, 5, 100)

    # Functions
    sigmoid = 1 / (1 + np.exp(-z))
    tanh = np.tanh(z)
    relu = np.maximum(0, z)

    plt.figure(figsize=(10, 6))

    # Use raw string r'' for LaTeX
    plt.plot(z, sigmoid, label=r"Sigmoid $\sigma(z)$", linewidth=2)
    plt.plot(z, tanh, label="Tanh", linewidth=2, linestyle="--")
    plt.plot(z, relu, label="ReLU", linewidth=2, linestyle="-.")

    plt.title("Activation Functions Comparison", fontsize=16)
    plt.xlabel("Input (z)", fontsize=14)
    plt.ylabel("Activation", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.axhline(0, color="black", linewidth=1)
    plt.axvline(0, color="black", linewidth=1)
    plt.ylim(-1.5, 2.0)
    plt.tight_layout()

    # Save as transparent PDF
    plt.savefig("activation_functions.pdf", transparent=True)
    plt.show()


def plot_optimization_landscape_min():
    # Visualization of Valley Seeking (Minimization)
    x = np.linspace(-2, 10, 1000)

    # Invert the function to create valleys (Minimization problem)
    y = -(np.sin(x) + np.sin((10.0 / 3.0) * x))

    plt.figure(figsize=(12, 6))
    plt.plot(x, y, label="Cost Function (Loss)", color="black")

    # Find valleys (peaks of -y)
    valleys, _ = find_peaks(-y)

    # 1. Global Minimum
    global_idx = valleys[np.argmin(y[valleys])]
    x_global, y_global = x[global_idx], y[global_idx]

    # 2. Local Minimum (Trap)
    sorted_valley_indices = valleys[np.argsort(y[valleys])]
    # Pick the second lowest valley if available
    local_idx = (
        sorted_valley_indices[1]
        if len(sorted_valley_indices) > 1
        else sorted_valley_indices[0]
    )
    # Cast to float to fix linter error
    x_local = float(x[local_idx])
    y_local = float(y[local_idx])

    # Plot points
    plt.scatter(
        [x_local], [y_local], color="red", s=100, label="Local Min (Trap)", zorder=5
    )
    plt.scatter(
        [x_global], [y_global], color="green", s=100, label="Global Min", zorder=5
    )

    # Annotation with curved arrow
    plt.annotate(
        "Stuck Here",
        xy=(x_local, y_local),
        xytext=(x_local + 2.0, y_local + 2.5),  # Moved further away for angle
        arrowprops=dict(
            facecolor="black",
            shrink=0.05,
            connectionstyle="arc3,rad=.2",  # Adds a slight curve
        ),
        fontsize=12,
    )

    plt.title("The Problem of Local Optima in Minimization", fontsize=16)
    plt.xlabel("Parameter Space (Weights)", fontsize=14)
    plt.ylabel("Cost / Loss", fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save as transparent PDF
    plt.savefig("optimization_landscape_min.pdf", transparent=True)
    plt.show()


def plot_sampling_strategies():
    N = 50

    # 1. Random Sampling
    rng = np.random.default_rng(42)
    random_pop = rng.uniform(0, 1, (N, 2))

    # 2. OBL (Opposition Based)
    initial_subset = random_pop[:10]
    opposite_subset = 1.0 - initial_subset

    # 3. Sobol Proxy
    x = np.linspace(0.1, 0.9, int(np.sqrt(N)))
    y = np.linspace(0.1, 0.9, int(np.sqrt(N)))
    grid_x, grid_y = np.meshgrid(x, y)
    sobol_proxy = np.column_stack((grid_x.ravel(), grid_y.ravel()))
    sobol_proxy += rng.uniform(-0.02, 0.02, sobol_proxy.shape)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Plot Random
    axes[0].scatter(random_pop[:, 0], random_pop[:, 1], c="blue", alpha=0.6)
    axes[0].set_title("Uniform Random", fontsize=14)
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1)

    # Plot OBL
    axes[1].scatter(
        initial_subset[:, 0], initial_subset[:, 1], c="blue", label="Original"
    )
    axes[1].scatter(
        opposite_subset[:, 0],
        opposite_subset[:, 1],
        c="red",
        marker="x",
        label="Opposite",
    )
    axes[1].plot(
        [initial_subset[:, 0], opposite_subset[:, 0]],
        [initial_subset[:, 1], opposite_subset[:, 1]],
        "k--",
        alpha=0.2,
    )
    axes[1].set_title("Opposition-Based", fontsize=14)
    axes[1].legend()
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)

    # Plot Sobol
    axes[2].scatter(sobol_proxy[:, 0], sobol_proxy[:, 1], c="green", alpha=0.6)
    axes[2].scatter(sobol_proxy[:, 0], sobol_proxy[:, 1], c='green', alpha=0.6)
    axes[2].set_title("Low-Discrepancy (Sobol)", fontsize=14)
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1)

    plt.tight_layout()

    # Save as transparent PDF
    plt.savefig("sampling_strategies.pdf", transparent=True)
    plt.show()


if __name__ == "__main__":
    plot_activation_functions()
    plot_optimization_landscape_min()
    plot_sampling_strategies()
