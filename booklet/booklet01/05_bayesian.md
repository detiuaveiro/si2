# Bayesian Agents and Probabilistic Reasoning

While logic-based agents provide a powerful framework for reasoning in structured environments, they often struggle with the messy, uncertain reality of the physical world. In a purely logical system, an agent requires an exhaustive list of preconditions to guarantee an action—a challenge known as the **Qualification Problem**. Furthermore, the **Laziness Problem** highlights the impracticality of accounting for every possible exception. To thrive in environments where knowledge is incomplete and observations are noisy, agents must shift from the binary certainty of logic to the numerical "degrees of belief" provided by **Probabilistic Reasoning**.

## From Certainty to Uncertainty

In logic, a sentence is either True, False, or Unknown. In contrast, a probabilistic agent assigns a probability between 0 and 1 to every state, representing its subjective uncertainty. This shift allows the agent to handle:
*   **Theoretical Ignorance**: Not knowing all the rules governing the environment.
*   **Practical Ignorance**: Not having enough sensors to observe the full state of the world.

The core of this approach is the **Bayesian** perspective, where probability is seen as an agent's belief that is updated as new evidence arrives. This is fundamentally different from the **Frequentist** view, which defines probability as the long-run frequency of an event.

### Random Variables and Distributions
We represent aspects of the world using **Random Variables** ($X$). Each variable has a **Sample Space** ($\Omega$)—the set of all possible outcomes. A **Probability Distribution** assigns a value to each outcome such that the sum of all probabilities is exactly 1.
$$\sum_{x \in \Omega} P(X=x) = 1$$

The **Law of Total Probability** allows an agent to determine the probability of an event $A$ by considering all the mutually exclusive ways it could occur:
$$P(A) = \sum_i P(A | B_i)P(B_i)$$

## The Heart of Bayesian Inference: Bayes' Rule

The most critical tool for a probabilistic agent is **Bayes' Rule**. It provides a mathematical mechanism for the agent to update its "World Model" based on new sensor data. It relates the **Prior** (what was known before) and the **Likelihood** (how well the evidence explains a cause) to the **Posterior** (the updated belief).

**Equation of Bayes' Rule**:
$$P(Cause | Effect) = \frac{P(Effect | Cause)P(Cause)}{P(Effect)}$$

**Example: The Noisy Sensor**
Consider an agent that must decide if a person is behind a door based on a noisy motion sensor. 
*   Prior: $P(Person) = 0.3$.
*   Likelihood (True Positive): $P(Sensor | Person) = 0.9$.
*   False Positive: $P(Sensor | \neg Person) = 0.2$.
If the sensor triggers, the agent applies Bayes' rule to find that the probability of a person being there has increased from 30% to approximately 66%, allowing it to make a more informed decision to open the door.

## Bayesian Networks

A **Bayesian Network** is a graphical model that represents the probabilistic relationships between variables. It consists of a **Directed Acyclic Graph (DAG)** where nodes are random variables and edges represent direct causal influences.

\begin{center}
\begin{tikzpicture}[node distance=2.5cm, auto, thick, >=stealth]
    \node (rain) [circle, draw, fill=blue!05] {Rain};
    \node (sprinkler) [circle, draw, below left=of rain, fill=orange!05] {Sprinkler};
    \node (grass) [circle, draw, below right=of rain, fill=green!05] {Wet Grass};
    
    \draw[->] (rain) -- node [left, font=\small] {Causes} (sprinkler);
    \draw[->] (rain) -- node [right, font=\small] {Causes} (grass);
    \draw[->] (sprinkler) -- node [below, font=\small] {Causes} (grass);
\end{tikzpicture}
\end{center}

The power of a Bayesian Network lies in its ability to factor the **Joint Probability Distribution** into smaller, local conditional probability tables (CPTs). This reduces the complexity of the problem from exponential to linear in many cases:
$$P(x_1, \dots, x_n) = \prod_{i=1}^{n} P(x_i | parents(x_i))$$

## Modeling Decisions over Time: Markov Processes and MDPs

Agents often operate in environments where decisions have long-term consequences. To prevent a "memory explosion," we often assume the **Markov Property**: the future depends only on the current state, not the past.

### Markov Decision Processes (MDP)
An MDP extends this idea by adding actions and rewards. It is defined by:
1.  **States (S)**: The set of possible situations.
2.  **Actions (A)**: What the agent can do.
3.  **Transition Model $P(s' | s, a)$**: The probability of reaching state $s'$ from $s$ given action $a$.
4.  **Reward Function $R(s, a, s')$**: The immediate payoff for a transition.

The goal of the agent is to find an **Optimal Policy** ($\pi^*$) that maximizes the **Expected Utility**. Because future rewards are uncertain, we use a **Discount Factor** ($\gamma \in [0, 1]$) to value immediate rewards more than distant ones.

**The Bellman Equation**:
The value of a state $V(s)$ is the maximum expected return the agent can achieve from that state:
$$V(s) = \max_a \sum_{s'} P(s'|s, a) [R(s, a, s') + \gamma V(s')]$$

\begin{center}
\begin{tikzpicture}[node distance=2.5cm, auto, thick, >=stealth]
    \node (s1) [circle, draw, fill=blue!05, minimum size=1cm] {$s$};
    \node (a1) [rectangle, draw, right=of s1, xshift=1cm, fill=orange!05] {$a_1$};
    \node (a2) [rectangle, draw, below=of a1, yshift=0.5cm, fill=orange!05] {$a_2$};
    \node (s_prime) [circle, draw, right=of a1, xshift=1cm, fill=green!05, minimum size=1cm] {$s'$};
    
    \draw[->] (s1) -- (a1);
    \draw[->] (s1) -- (a2);
    \draw[->] (a1) -- node [above, font=\small] {$P(s'|s, a_1)$} (s_prime);
    \draw[->] (s_prime.east) -- ++(1.5,0) node [right, font=\small\itshape] {Reward $R$};
\end{tikzpicture}
\end{center}

## Training and Implementation

Building a Bayesian agent involves learning both the structure of the network and the values in the CPTs.
*   **Maximum Likelihood Estimation (MLE)**: Counting observations to fill the tables.
*   **Monte Carlo Methods**: Running thousands of random simulations (trajectories) to estimate the value of states when the transition model is unknown.

Modern tools like **pgmpy** (for Bayesian Networks) and **Gymnasium** (for MDPs and Reinforcement Learning) allow developers to implement these complex mathematical models efficiently. By separating the "Prior" knowledge from the "Evidence" gathered by sensors, Bayesian agents can make rational decisions in an inherently uncertain world.
