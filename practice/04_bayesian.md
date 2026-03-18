---
title: Probabilistic Reasoning 
---

# Practice Sheet: Bayesian Agents

## Objectives
- Transition from static Rule Engines to dynamic **Probabilistic Models**.
- Review foundational probability and introduce the **Markov Property**.
- Implement **Bayesian Inference** for classification (Spam Filtering).
- Use **Monte Carlo Methods** to evaluate state values through random sampling.
- Understand **Temporal Credit Assignment** and the role of the Discount Factor.
- Explore **Reward Shaping** to solve sparse-reward environments (Flappy Bird).
- Balance **Exploration vs. Exploitation** using Boltzmann Temperature.

---

## Theory Refresh – Probabilities & Processes

Before building agents, we must establish how they view uncertainty and time.

**1. Bayes' Theorem:**
The core mechanism for updating beliefs based on new evidence.
$$P(A|B)=\frac{P(B|A)P(A)}{P(B)}$$
* **Prior $P(A)$:** What the agent believes before seeing evidence.
* **Likelihood $P(B|A)$:** The probability of observing this evidence if the belief is true.
* **Posterior $P(A|B)$:** The updated belief.

**2. The Markov Property:**
When transitioning from single decisions to sequential games, we rely on the Markov Property. 
It states that the future depends *only* on the current state, not on the sequence of events that preceded it.
Modeling environments as **Markov Processes** allows our probabilistic agents to calculate the value of their current situation without needing an infinite memory of the past. 
This concept will be the bedrock of your next core topic.

---

## Exercise 1: The "Hot or Cold" Secret Number

Before diving into complex games, you must understand how a single probability distribution evolves with evidence.

**The Scenario:** An agent must guess a secret number $N \in [1, 100]$. The only feedback provided is "Hotter" (closer than the previous guess) or "Colder" (further away).

**Your Task:**
1. **Initialize the Prior:** Create a uniform probability distribution $P(N)$ where every number has a $1\%$ chance.
2. **The Likelihood Function:** Write a function that updates the distribution based on a guess $g_t$ and the feedback. 
   - If "Hotter," increase the probability of all $n$ where $|n - g_t| < |n - g_{t-1}|$.
3. **Inference:** In each step, the agent should pick the number with the **Maximum A Posteriori (MAP)** probability.
4. **Observe Convergence:** Watch how the probability "peak" narrows as more evidence is collected.

---

## Exercise 2: Tic-Tac-Toe

In this exercise, you will train an agent to play Tic-Tac-Toe using a Lookup Table of probability values.

**Your Task:**
1. **State Representation:** Implement a `get_hash()` function that converts a **3x3** board into a unique string key.
2. **The Probability Table:** Initialize a dictionary where the agent stores the probability ("worth") of every board position it encounters.
3. **PT Update:** Use the following formula to update the probability of a state $S_t$ immediately after reaching state $S_{t+1}$:
   $$V(S_t)\leftarrow V(S_t)+\alpha[\gamma V(S_{t+1})-V(S_t)]$$
   *Where $\alpha$ is the learning rate and $\gamma$ is the discount factor.*
4. **Self-Play:** Run the training loop for 1k, 10k, 100k epochs. Ensure the agent plays against a version of itself to discover defensive maneuvers.

---

## Exercise 3: Naive Bayes Spam Filter

Shift from games to text classification. 
You will build a filter that uses the **Multivariate Bernoulli** model to identify spam.

**Your Task:**
1. **Preprocessing Pipeline:** - Use `nltk` to tokenize and POS-tag messages.
   - Implement **Lemmatization** (e.g., converting "winning" and "wins" to "win") to reduce the feature space.
2. **Training (Log-Space):** To avoid numerical underflow, calculate probabilities in log-space:
   $$\ln P(Spam | Words) \propto \ln P(Spam) + \sum \ln P(Word | Spam)$$
3. **Laplace Smoothing ($k$):** Ensure that a word never seen before doesn't result in a $0\%$ probability by adding $k=1$ to your counts.
4. **Evaluation:** Compute the **Accuracy** and **Precision** of your filter using the provided test dataset.

---

## Exercise 4: Flappy Bird

In many environments, the agent only receives a **Sparse Reward**—a simple "Win/Loss" signal at the very end of an interaction (like passing a pipe).
This makes learning incredibly slow. You will implement **Continuous Reward Shaping** to provide dense, step-by-step guidance.

**The Scenario:**
The agent must decide to `CLICK` or `IDLE` based on a binned state of `(vertical_dist_to_gap, velocity)`.

**Your Task:**
1. **Informed Prior:** Initialize your Bayesian table with a "Physics Prior." If the bird is above the gap (**d < 0**), initialize the probability of `IDLE` at **90%**.
2. **Reward Shaping (The "Magnet"):** Instead of waiting to pass the pipe, calculate an `alignment_reward` every single frame:
   $$R_{align}=\max(0,1-\frac{|bird\_y-gap\_y|}{100})$$
3. **Update Logic:** Update the agent per frame using this alignment reward. This provides a "gradient" that pulls the bird toward the center of the pipe even before it successfully passes one.
4. **Exploration Decay:** Implement a temperature **T** for Boltzmann sampling to balance exploring new moves vs. exploiting known good moves:
   $$P(action)=\frac{e^{Q(s,a)/T}}{\sum e^{Q(s,a')/T}}$$
   Start with **T=1.0** (random) and decay it to **T=0.01** (deterministic) over 1,000 epochs.
