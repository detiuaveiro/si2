# Deep Learning Exercises Summary & RL Agent Strategy

This document summarizes the reinforcement learning (RL) ready exercises in `./support/05_deep_learning/` and outlines the strategy for implementing agents for each.

## Exercise Overview

| Exercise | Important Parts | Current Method |
| :--- | :--- | :--- |
| **ex03_hot_cold** | Number guessing game (1-100) with binary search expert. | Behavioral Cloning (MLP) |
| **ex04_bouncing_ball** | Paddle control to follow a bouncing ball (State: `[bx, by, bvx, bvy, px]`). | Behavioral Cloning (MLP) |
| **ex05_tic_tac_toe** | 3x3 board game against a Minimax expert. | Behavioral Cloning (MLP) |
| **ex06_maze** | Pathfinding in a 10x10 grid with local perception. | Behavioral Cloning (CNN/Hybrid) |
| **ex07_snake** | Classic Snake game using visual state (10x10x3 tensor). | Behavioral Cloning (CNN) |

---

## RL Agent Strategies

We will select one method (Classical RL, Deep RL, or Neuroevolution) for each task, avoiding heavy libraries and using **Keras + JAX**.

### 1. ex03_hot_cold -> Classical RL (Q-Learning)
*   **Justification**: The state space (1-100) is small enough for a tabular approach.
*   **Implementation**: State = `[current_low, current_high]`. Action = `guess`. Reward = -1 per turn, +100 for correct guess. A simple **Q-Table** will easily converge to binary search logic.

### 2. ex04_bouncing_ball -> Deep RL (DQN)
*   **Justification**: The state is continuous (ball and paddle positions/velocities), making tabular RL (Curse of Dimensionality) difficult.
*   **Implementation**: Use **DQN** with a small MLP (Keras+JAX). Experience Replay and Target Networks are needed to stabilize the moving paddle. Reward +1 for every frame the ball is above the paddle.

### 3. ex05_tic_tac_toe -> Classical RL (Q-Learning)
*   **Justification**: With only $3^9 = 19,683$ possible states, Tic-Tac-Toe is perfect for tabular RL.
*   **Implementation**: Use a **Q-Table** where keys are board strings. Reward +1 for win, 0 for draw, -1 for loss. Train via self-play.

### 4. ex06_maze -> Deep RL (DQN)
*   **Justification**: While the grid is 10x10, the "local perception" and goal-seeking nature benefit from function approximation to generalize across different maze layouts.
*   **Implementation**: Use a **DQN** with the 3x3 local grid as input. Reward +10 for reaching the goal, -0.1 for every step (to find the shortest path).

### 5. ex07_snake -> Neuroevolution
*   **Justification**: Deep RL (PPO/DQN) for Snake is standard, but Neuroevolution is extremely effective for this "survival" task, as seen in the flappy-bird examples.
*   **Implementation**: Use a small CNN as the "brain". Fitness = Score (length) + Time survived. Evolve weights using a simple Genetic Algorithm (Selection + Mutation).

---

## Implementation Notes (Keras + JAX)
*   **Deep RL**: Use `keras.Model` for the Q-Network. Implement a simple `ReplayBuffer` using `collections.deque`.
*   **Neuroevolution**: Maintain a list of `keras.Model` objects. Fitness evaluation can be batch-processed for speed using JAX's vectorization if needed.
*   **Environment Interaction**: All agents should follow a standard `step(action) -> state, reward, done` interface to keep the code modular.
