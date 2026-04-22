---
title: Machine Learning for Agents
---

# Part 1: The Foundations of Learning

## What is Machine Learning?
* **Definition**: A field of AI that provides systems the ability to automatically learn and improve from experience without being explicitly programmed.
* **The "Experience" $(E)$**: Data from the environment, historical logs, or sensor streams.
* **The "Task" $(T)$**: Predicting an outcome, classifying an object, or making a decision.
* **The "Performance" $(P)$**: A metric to measure how well the agent is doing (Accuracy, RMSE, Reward).
* **Shallow ML**: Traditional algorithms that typically require manual feature engineering (e.g., KNN, SVM, DT).

## The Master Algorithm: The Five Tribes i

*Based on Pedro Domingos' "The Master Algorithm", ML can be categorized into 5 tribes based on their core philosophy:*

| Tribe | Philosophy | Core Algorithm |
| :--- | :--- | :--- |
| **Symbolists** | Logic, Philosophy | Inverse Deduction |
| **Connectionists** | Neuroscience | Backpropagation |
| **Evolutionaries** | Evolutionary Biology | Genetic Programming |
| **Bayesians** | Statistics | Probabilistic Inference |
| **Analogizers** | Geometry, Similarity | Kernel Machines (SVM) |

*The "Master Algorithm" is the ultimate learner that would combine all these approaches.*

## The Master Algorithm: The Five Tribes ii
\centering
\begin{tikzpicture}[node distance=3cm, auto, thick, scale=0.8, every node/.style={transform shape}]
\node[draw, circle, fill=blue!20, minimum size=2.5cm, text width=2cm, align=center] (S) at (90:4) {\textbf{Symbolists}\\(Logic)};
\node[draw, circle, fill=red!20, minimum size=2.5cm, text width=2cm, align=center] (C) at (18:4) {\textbf{Connectionists}\\(Neurons)};
\node[draw, circle, fill=green!20, minimum size=2.5cm, text width=2cm, align=center] (B) at (306:4) {\textbf{Bayesians}\\(Probability)};
\node[draw, circle, fill=yellow!20, minimum size=2.5cm, text width=2cm, align=center] (A) at (234:4) {\textbf{Analogizers}\\(Similarity)};
\node[draw, circle, fill=orange!20, minimum size=2.5cm, text width=2cm, align=center] (E) at (162:4) {\textbf{Evolutionaries}\\(DNA)};
\draw[<->, dashed, gray] (S) -- (C); \draw[<->, dashed, gray] (C) -- (B);
\draw[<->, dashed, gray] (B) -- (A); \draw[<->, dashed, gray] (A) -- (E);
\draw[<->, dashed, gray] (E) -- (S);
\node[draw, star, star points=5, star point ratio=2.25, fill=white, minimum size=1.5cm] at (0,0) {Master};
\end{tikzpicture}

# Part 2: Learning Taxonomies

## Taxonomy I: Expected Response

* **Supervised Learning**: Learning from labeled data ($X, y$). Mapping $f: X \to y$.
  * *Classification*: Discrete labels (e.g., "Safe" vs "Danger").
  * *Regression*: Continuous values (e.g., distance to target).
* **Unsupervised Learning**: Learning from unlabeled data ($X$). Structure discovery.
  * *Clustering*: Grouping similar environment states.
  * *Dimensionality Reduction*: Compressing complex sensor data.
* **Reinforcement Learning**: Learning via rewards/penalties.
  * *Focus*: Sequential decision making (next class topic).

## Taxonomy II: Discriminative vs Generative Models

:::::::::::::: {.columns}
::: {.column width="50%"}
**Discriminative Models**

* Models the boundary: $P(y|X)$.
* Focused on classification tasks.
* "What is the difference between A and B?"
:::
::: {.column width="50%"}
**Generative Models**

* Models the distribution: $P(X, y)$.
* Can generate new data points.
* "What does a typical A look like?"
:::
::::::::::::::

\vspace{0.3cm}
\centering
\begin{tikzpicture}[scale=0.6]
% Discriminative
\begin{scope}[xshift=-4.5cm]
\draw[->] (0,0) -- (4,0) node[right] {$x_1$};
\draw[->] (0,0) -- (0,3) node[above] {$x_2$};
\foreach \p in {(0.5,2.0), (1.0,2.5), (0.5,2.5)} \fill[blue] \p circle (3pt);
\foreach \p in {(2.5,0.5), (3.0,1.0), (2.5,0.0)} \fill[red] \p circle (3pt);
\draw[ultra thick, black] (0, 0.5) -- (3.5, 2.5); 
\node at (2, -0.7) {\small Boundary};
\end{scope}
% Generative
\begin{scope}[xshift=4.5cm]
\draw[->] (0,0) -- (4,0) node[right] {$x_1$};
\draw[->] (0,0) -- (0,3) node[above] {$x_2$};
\draw[blue, fill=blue, opacity=0.2] (0.8,2.3) circle (0.7);
\draw[red, fill=red, opacity=0.2] (2.8,0.5) circle (0.7);
\foreach \p in {(0.5,2.0), (1.0,2.5), (0.5,2.5)} \fill[blue] \p circle (3pt);
\foreach \p in {(2.5,0.5), (3.0,1.0), (2.5,0.0)} \fill[red] \p circle (3pt);
\node at (2, -0.7) {\small Distributions};
\end{scope}
\end{tikzpicture}

## Taxonomy III: Offline vs Online Learning

\centering
\begin{tikzpicture}[auto, thick, node distance=2cm, >=latex]
% Offline
\node[draw, rectangle, rounded corners, fill=gray!10, minimum height=1cm, text width=2cm, align=center] (DB) {Static Dataset};
\node[draw, rectangle, right of=DB, node distance=3.5cm, fill=blue!10, minimum height=1cm, text width=2cm, align=center] (Train) {Train Model Once};
\node[draw, rectangle, right of=Train, node distance=3.5cm, fill=green!10, minimum height=1cm, text width=2cm, align=center] (Deploy) {Deploy to Agent};
\draw[->] (DB) -- (Train);
\draw[->] (Train) -- (Deploy);
\node[above of=Train, node distance=1.2cm] {\textbf{Offline (Batch) Learning}};
% Online
\begin{scope}[yshift=-3.5cm]
\node[draw, rectangle, fill=gray!10, minimum height=1cm, text width=2cm, align=center] (Stream) {Data Stream (Live)};
\node[draw, rectangle, right of=Stream, node distance=3.5cm, fill=blue!10, minimum height=1cm, text width=2cm, align=center] (Model) {Adaptive Model};
\node[draw, rectangle, right of=Model, node distance=3.5cm, fill=green!10, minimum height=1cm, text width=2cm, align=center] (Pred) {Continuous Action};
\draw[->] (Stream) -- node[above]{$x_t$} (Model);
\draw[->] (Model) -- (Pred);
\draw[->] (Pred) to[out=270, in=270, looseness=0.8] node[below]{Update from Feedback} (Model);
\node[above of=Model, node distance=1.2cm] {\textbf{Online (Incremental) Learning}};
\end{scope}
\end{tikzpicture}

# Part 3: Decision Boundaries and Representation

## The Decision Boundary i

* **Definition**: A hypersurface that partitions the underlying vector space into sets, one for each class.
* **The Limit of Learning**: An agent's capability is strictly bounded by the complexity of the boundaries its model can represent.
* **Representational Capacity**: If the true relationship is a circle but the model only knows lines, it can never achieve 100% accuracy.

\centering
\begin{tikzpicture}[scale=0.9]
    % Linear
    \begin{scope}[xshift=-3cm]
    \draw[->] (0,0) -- (2.5,0); \draw[->] (0,0) -- (0,2.5);
    \draw[red, ultra thick] (0.2, 2.3) -- (2.3, 0.2);
    \node at (1.25, -0.5) {Linear (Simple)};
    \end{scope}
    % Non-linear
    \begin{scope}[xshift=3cm]
    \draw[->] (0,0) -- (2.5,0); \draw[->] (0,0) -- (0,2.5);
    \draw[red, ultra thick, smooth cycle, tension=0.7] plot coordinates {(0.5,0.5) (0.5,2) (2,2) (2,0.5)};
    \node at (1.25, -0.5) {Non-linear (Complex)};
    \end{scope}
\end{tikzpicture}

## The Decision Boundary ii: Model Fit
\centering
\begin{tikzpicture}[scale=0.6, >=latex]
    \def\pts{(0.5, 0.6), (1.0, 1.1), (1.5, 2.4), (2.0, 3.8), (2.5, 6.1)}
    % Underfit
    \begin{scope}[xshift=-6cm]
        \draw[->] (0,0) -- (3,0); \draw[->] (0,0) -- (0,7);
        \foreach \p in \pts \fill \p circle (3pt);
        \draw[red, thick] (0,0.5) -- (3,4.5);
        \node[align=center] at (1.5, -1.2) {\textbf{Underfit}\\(High Bias)};
    \end{scope}
    % Good Fit
    \begin{scope}[xshift=0cm]
        \draw[->] (0,0) -- (3,0); \draw[->] (0,0) -- (0,7);
        \foreach \p in \pts \fill \p circle (3pt);
        \draw[blue, thick, smooth, domain=0:2.6] plot (\x, {0.9*\x*\x + 0.5});
        \node[align=center] at (1.5, -1.2) {\textbf{Good Fit}\\(Generalizable)};
    \end{scope}
    % Overfit
    \begin{scope}[xshift=6cm]
        \draw[->] (0,0) -- (3,0); \draw[->] (0,0) -- (0,7);
        \foreach \p in \pts \fill \p circle (3pt);
        \draw[green!60!black, thick, smooth] plot coordinates {(0,0) (0.5,0.6) (0.7,2) (1.0,1.1) (1.2,4) (1.5,2.4) (1.8,6) (2.0,3.8) (2.3,7) (2.5,6.1) (2.8,4)};
        \node[align=center] at (1.5, -1.2) {\textbf{Overfit}\\(High Variance)};
    \end{scope}
\end{tikzpicture}

# Part 4: Fundamental Limitations

## Limitation I: Max Expected Performance
* In real-world agent environments, classes often overlap in feature space.
* **Bayes Error**: The minimum possible error rate.
* Overlap means that for some $X$, the same observation could belong to multiple classes.

\centering
\begin{tikzpicture}[scale=1.2]
    \draw[->] (-3,0) -- (5,0) node[right] {$x$};
    \draw[->] (0,-0.2) -- (0,1.8) node[above] {$P(x|y)$};
    
    \draw[blue, thick, smooth, domain=-3:3, samples=100] plot (\x, {1.4*exp(-(\x)^2/2)});
    \draw[red, thick, smooth, domain=-1:5, samples=100] plot (\x, {1.4*exp(-(\x-2)^2/2)});
    
    \node[blue] at (-1.5, 1.2) {Class A};
    \node[red] at (3.5, 1.2) {Class B};
    
    \begin{scope}
        \clip plot[domain=-3:3, smooth, samples=100] (\x, {1.4*exp(-(\x)^2/2)}) -- (3,0) -- (-3,0) -- cycle;
        \fill[purple, opacity=0.3] plot[domain=-1:5, smooth, samples=100] (\x, {1.4*exp(-(\x-2)^2/2)}) -- (5,0) -- (-1,0) -- cycle;
    \end{scope}
    
    \node[font=\small] at (1, 0.3) {Overlap};
\end{tikzpicture}

## Limitation II: The Curse of Dimensionality
* As the number of features increases, the volume of the space grows exponentially.
* Density of samples decreases, and points become isolated in corners.
* The "average distance" to neighbors increases significantly.

\centering
\begin{tikzpicture}[scale=1.2, >=latex]
    % 1D
    \begin{scope}[xshift=0cm]
        \draw[thick] (0,0) -- (1.5,0);
        \node at (0.75, -0.2) {1D};
    \end{scope}
    
    % 2D
    \begin{scope}[xshift=3cm]
        \draw[thick] (0,0) rectangle (1.5,1.5);
        \node at (0.75, -0.2) {2D};
    \end{scope}
    
    % 3D
    \begin{scope}[xshift=6cm]
        \draw[thick] (0,0,0) -- (1.5,0,0) -- (1.5,1.5,0) -- (0,1.5,0) -- cycle;
        \draw[thick] (0,0,-1.5) -- (1.5,0,-1.5) -- (1.5,1.5,-1.5) -- (0,1.5,-1.5) -- cycle;
        \draw[thick] (0,0,0) -- (0,0,-1.5); \draw[thick] (1.5,0,0) -- (1.5,0,-1.5);
        \draw[thick] (1.5,1.5,0) -- (1.5,1.5,-1.5); \draw[thick] (0,1.5,0) -- (0,1.5,-1.5);
        \node at (0.75, -0.2) {3D};
    \end{scope}
\end{tikzpicture}

## Limitation III: No Free Lunch Theorem
* **Definition**: No single machine learning algorithm is universally better than any other across all possible problems.
* **Implication for Agents**: An agent optimized for a "Maze" environment may perform poorly in an "Open Field" without retraining or re-tuning.

\centering
\begin{tikzpicture}[scale=0.7]
    \draw[->] (0,0) -- (5,0) node[right] {Problem Space};
    \draw[->] (0,0) -- (0,3) node[above] {Performance};
    \draw[blue, ultra thick] plot [smooth] coordinates {(0.5,2.5) (2.5,1) (4.5,0.5)} node[right] {Algo A};
    \draw[red, ultra thick] plot [smooth] coordinates {(0.5,0.5) (2.5,1) (4.5,2.5)} node[right] {Algo B};
    \node[fill=gray!10, draw] at (2.5, -1) {Inductive Bias determines success};
\end{tikzpicture}

# Part 5: Models

## KNN i: Intuition and Diagram
* **Core Idea**: "Similarity implies the same class".
* **Lazy Learning**: No explicit training phase; just store the data.
* **Classification**: Query point takes the majority label of its $k$ closest neighbors.

\centering
\begin{tikzpicture}[scale=1]
    \foreach \p in {(0.4,1.8), (0.9,2.2), (1.3,1.4)} \fill[blue] \p circle (3pt);
    \foreach \p in {(2.7,0.4), (3.2,1.0), (2.9,0.7)} \fill[red] \p circle (3pt);
    \node[draw, star, star points=5, fill=yellow, minimum size=0.5cm] (Q) at (2.0,1.3) {};
    \draw[dashed, thick] (Q) circle (1.25cm);
    \node[above] at (Q) {$x_q$ (Query)};
    \draw[->, gray, thin] (1.3,1.4) -- (Q);
    \draw[->, gray, thin] (2.7,0.4) -- (Q);
    \draw[->, gray, thin] (3.2,1.0) -- (Q);
    \draw[->, gray, thin] (2.9,0.7) -- (Q);
    \node at (2.0, -0.5) {\small $k=3 \implies$ Red Wins};
\end{tikzpicture}

## KNN ii: Mathematical Formulation
* **Distance Metric**: Usually Euclidean distance in $d$-dimensional space.
$$ d(x, y) = \sqrt{\sum_{i=1}^d (x_i - y_i)^2} $$
* **Classification Rule**: Let $N_k(x)$ be the set of $k$ nearest training samples to query point $x$.
$$ \hat{y} = \arg\max_{c \in \mathcal{C}} \sum_{x_i \in N_k(x)} I(y_i = c) $$
* **Regression Rule**:
$$ \hat{y} = \frac{1}{k} \sum_{x_i \in N_k(x)} y_i $$

## KNN iii: Algorithms and Usage

* **Algorithm**:
    1.  **Training**: Store all labeled training pairs $(X, Y)$ in memory.
    2.  **Inference**: For each query point $x_q$:
        * Calculate distance to all $N$ stored samples.
        * Sort samples and identify the $k$ nearest neighbors.
        * Apply majority vote (Classification) or mean (Regression).
* **Real-World Usage**:
    * **Recommendation Systems**: "Users like you also watched...".
    * **Agent Use**: Memory-based agents that recall the outcome of similar past states to decide current actions.

## KNN iv: Pros and Cons

* **Pros**:
    * Zero training time ($O(1)$).
    * Naturally handles multi-class problems.
    * Highly intuitive and non-parametric.
* **Cons**:
    * **Inference is slow**: $O(N \cdot d)$ per query.
    * **High Memory**: Must store the entire dataset.
    * **Curse of Dimensionality**: Performance degrades as dimensions increase.
    * Sensitive to irrelevant features and data scale.

## Naive Bayes i: Intuition and Diagram

* **Core Idea**: Uses Bayes' Theorem to find the probability of a class given the input features.
* **The "Naive" Part**: Assumes that every feature is completely independent of every other feature, given the class label.

\centering
\begin{tikzpicture}[node distance=2cm, auto, thick, >=latex]
    \node[draw, circle, fill=blue!20, minimum size=1.5cm, align=center] (Y) {Class\\$Y$};
    \node[draw, circle, fill=gray!10, below left of=Y, node distance=2.5cm] (X1) {$X_1$};
    \node[draw, circle, fill=gray!10, below of=Y, node distance=2.2cm] (X2) {$X_2$};
    \node[draw, circle, fill=gray!10, below right of=Y, node distance=2.5cm] (Xn) {$X_n$};
    \draw[->] (Y) -- (X1); \draw[->] (Y) -- (X2); \draw[->] (Y) -- (Xn);
    \node at (0, -3.5) {\small $P(X_1, X_2 | Y) = P(X_1|Y)P(X_2|Y)$};
\end{tikzpicture}

## Naive Bayes ii: Mathematical Formulation

* **Bayes' Theorem**:
$$ P(y | X) = \frac{P(X | y)P(y)}{P(X)} $$
* **Independence Assumption**:
$$ P(x_1, \dots, x_n | y) = \prod_{i=1}^n P(x_i | y) $$
* **Decision Rule**:
$$ \hat{y} = \arg\max_{y} \left( P(y) \prod_{i=1}^n P(x_i | y) \right) $$
*We ignore $P(X)$ because it's constant for all classes.*

## Naive Bayes iii: Algorithms and Usage

* **Algorithm**:
    1.  **Training**: Count occurrences to estimate class priors $P(y)$ and conditional likelihoods $P(x_i|y)$.
    2.  **Inference**: For new input $X_q$, multiply the learned probabilities and pick the class that maximizes the result.
* **Real-World Usage**:
    * **Spam Filtering**: Word probabilities determining if an email is junk.
    * **Agent Use**: Sensor Fusion. An agent treating different sensor readings as independent evidence for the state of the world.

## Naive Bayes iv: Pros and Cons

* **Pros**:
    * Extremely fast training and inference.
    * Works well with small datasets.
    * Scalable to very high-dimensional feature spaces.
* **Cons**:
    * **Independence Fallacy**: In real life, features are often correlated (e.g., in a car, speed and RPM are not independent).
    * **Zero Frequency Problem**: If a combination was never seen in training, the probability becomes zero (can be fixed with Laplace Smoothing).

## Perceptron i: Intuition and Diagram

* **Core Idea**: A mathematical model of a single biological neuron that performs binary classification.
* **Mechanism**: It sums weighted inputs and checks if the result exceeds a threshold.

\centering
\begin{tikzpicture}[node distance=1.5cm, auto, thick, >=latex]
    \node (x1) at (-2, 1.2) {$x_1$};
    \node (x2) at (-2, 0) {$x_2$};
    \node (xn) at (-2, -1.2) {$x_n$};
    \node[draw, circle, fill=gray!20, minimum size=1cm] (sum) at (0,0) {$\sum$};
    \node[draw, rectangle, fill=blue!10, minimum height=1cm, right of=sum, node distance=2.5cm] (act) {Step Function};
    \node (out) at (6,0) {$\hat{y} \in \{0,1\}$};
    \draw[->] (x1) -- node[above] {$w_1$} (sum);
    \draw[->] (x2) -- node[above] {$w_2$} (sum);
    \draw[->] (xn) -- node[above] {$w_n$} (sum);
    \draw[->] (sum) -- node[above] {$z$} (act);
    \draw[->] (act) -- (out);
\end{tikzpicture}

## Perceptron ii: Mathematical Formulation

* **Input Combination**:
$$ z = \sum_{i=1}^n w_i x_i + b = \mathbf{w}^T \mathbf{x} + b $$
* **Step Activation Function**:
$$ \hat{y} = \begin{cases} 1 & \text{if } z \ge 0 \\ 0 & \text{if } z < 0 \end{cases} $$
* **Update Rule (Learning)**:
$$ w_i \leftarrow w_i + \eta (y - \hat{y}) x_i $$
*Where $\eta$ is the learning rate, $y$ is the true label, and $\hat{y}$ is the prediction.*

## Perceptron iii: Algorithms and Usage

* **Algorithm**:
    1.  Initialize weights $\mathbf{w}$ to small random values or zeros.
    2.  For each training sample $(X, y)$:
        * Predict $\hat{y}$ using current weights.
        * If $\hat{y} \neq y$, update the weights using the error signal.
    3.  Repeat until weights stabilize or error is minimized.
* **Real-World Usage**:
    * **Building Block**: Basis of modern Neural Networks and Deep Learning.
    * **Agent Use**: Simple reflex agents (e.g., move if average light intensity $>$ threshold).

## Perceptron iv: Pros and Cons

* **Pros**:
    * Extremely simple and computationally efficient.
    * Guaranteed to converge **if** the data is linearly separable.
* **Cons**:
    * **Linear Limitation**: Cannot solve problems that aren't separable by a line (like the XOR problem).
    * Can take a long time to converge on noisy data.
    * Hard output (0 or 1) provides no measure of confidence.

## Logistic Regression i: Intuition and Sigmoid
* **Core Idea**: Outputs a **probability** instead of a hard class label.
* **Activation**: Uses the Sigmoid function to map any value into the range $[0, 1]$.

\centering
\begin{tikzpicture}[scale=0.8]
    \draw[->] (-4,0) -- (4,0) node[right] {$z$};
    \draw[->] (0,-0.2) -- (0,1.5) node[above] {$\sigma(z)$};
    \draw[blue, ultra thick, smooth, domain=-4:4] plot (\x, {1/(1+exp(-\x))});
    \draw[dashed, gray] (-4,1) -- (4,1);
    \node[left] at (0,1) {1.0};
    \node[left] at (0,0.5) {0.5};
    \node[below] at (2, 0.8) {\small $\sigma(z) = \frac{1}{1+e^{-z}}$};
\end{tikzpicture}

## Logistic Regression ii: Mathematical Formulation
* **Probability Model**:
$$ P(y=1 | x) = \sigma(\mathbf{w}^T \mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x} + b)}} $$
* **Binary Classification**: We predict class 1 if $P(y=1|x) \ge 0.5$.
* **Cost Function (Log Loss)**:
$$ J(\mathbf{w}) = -\frac{1}{m} \sum_{i=1}^m [y_i \log(\hat{y}_i) + (1-y_i) \log(1-\hat{y}_i)] $$

## Logistic Regression iii: Algorithms and Usage
* **Algorithm**:
    1.  Initialize weights $\mathbf{w}$.
    2.  Use **Gradient Descent** to find the weights that minimize the Log Loss.
    3.  Iteratively update: $\mathbf{w} \leftarrow \mathbf{w} - \eta \nabla J(\mathbf{w})$.
* **Real-World Usage**:
    * **Medical Diagnosis**: Probability of having a disease based on symptoms.
    * **Ad-Click Prediction**: Likelihood a user will click on an ad.
    * **Agent Use**: Uncertainty-aware agents. Deciding to "Attack" if probability of winning $> 0.75$.

## Logistic Regression iv: Pros and Cons
* **Pros**:
    * Provides calibrated probabilities (confidence levels).
    * Robust to noise and less prone to overfitting than complex models.
    * Mathematically well-founded and interpretable.
* **Cons**:
    * Still fundamentally a **linear classifier**.
    * Assumes a linear relationship between features and the log-odds of the outcome.

## Decision Trees i: Intuition and Diagram
* **Core Idea**: Uses a tree-like model of decisions and their possible consequences.
* **Recursive Partitioning**: Splits the data into subsets based on feature values to maximize purity.

\centering
\begin{tikzpicture}[level distance=1.2cm, sibling distance=3cm, every node/.style={draw, rectangle, rounded corners, fill=gray!10, text width=2cm, align=center}]
\node {\small Target Visible?}
child {node {\small Dist < 5m?}
child {node[fill=red!20] {\small Attack}}
child {node[fill=blue!20] {\small Chase}}
}
child {node[fill=green!20] {\small Patrol}};
\end{tikzpicture}

## Decision Trees ii: Mathematical Formulation
* **Entropy**: Measure of disorder in a set $S$.
$$ H(S) = - \sum_{i=1}^c p_i \log_2(p_i) $$
* **Information Gain**: Difference in entropy before and after a split on attribute $A$.
$$ IG(S, A) = H(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} H(S_v) $$
* **Gini Impurity**: Alternative split metric.
$$ Gini(S) = 1 - \sum_{i=1}^c p_i^2 $$

## Decision Trees iii: Algorithms and Usage
* **Algorithm (ID3/C4.5)**:
    1.  Select the "best" attribute using Information Gain.
    2.  Split the dataset into subsets based on attribute values.
    3.  Repeat recursively for each branch until leaf nodes (pure classes) are reached or a stopping criterion is met.
* **Real-World Usage**:
    * **Credit Scoring**: Determining loan eligibility.
    * **Clinical Decision Support**: Diagnosis flowcharts.
    * **Agent Use**: Behavior Trees and human-interpretable policy generation.

## Decision Trees iv: Pros and Cons
* **Pros**:
    * Highly interpretable (White-box model).
    * Handles both numerical and categorical data.
    * Captures non-linear relationships.
* **Cons**:
    * **Overfitting**: Very prone to building overly complex trees (needs pruning).
    * **Instability**: Small changes in data can lead to a completely different tree structure.
    * High-variance model.

# Part 6: ML Examples for Agents

## Example: Hot/Cold Number Guess

* **Approach**: Use **Regression** to learn the mapping from (Guess, Feedback) to (Target).
* **Agent Logic**: Predicts the target location based on historical distance responses.

## Example: Tic-Tac-Toe

* **Approach**: Use a **Classifier** (e.g., Perceptron or DT) to evaluate the "strength" of a board state.
* **Agent Strategy**: Evaluates all next moves and picks the one with the highest Win probability.

# Part 7: Hybrid Architectures

## Perception vs. Reasoning

* **ML Layer**: Excellent at handling noisy, raw data (pixels, sound, lidar) to identify abstract objects.
* **Logic Layer**: Excellent at high-level planning, safety rules, and strategic reasoning.

\centering
\begin{tikzpicture}[node distance=3.2cm, auto, thick, >=stealth]
\node[draw, rounded corners, fill=blue!10, text width=2.4cm, align=center] (Sensors) {Environment\\(Raw Data)};
\node[draw, rounded corners, fill=red!10, right of=Sensors, text width=2.4cm, align=center] (ML) {Perception\\(ML Model)};
\node[draw, rounded corners, fill=green!10, right of=ML, text width=2.4cm, align=center] (Logic) {Reasoning\\(Rule Engine)};
\node[draw, circle, fill=yellow!10, right of=Logic, node distance=2.5cm] (Action) {Act};
\draw[->, out=20, in=160] (Sensors) to node[above] {\small Pixels} (ML);
\draw[->, out=20, in=160] (ML) to node[above] {\small Objects} (Logic);
\draw[->, out=20, in=160] (Logic) to node[above] {\small Plan} (Action);
\end{tikzpicture}

## Hybrid Model Examples

* **Self-Driving Car**:
    * **ML**: Detects "Stop Sign" from camera feed.
    * **Logic**: If Sign detected AND Dist $<$ 5m, THEN activate Brake.
* **NPC Game Agent**:
    * **ML**: Predicts the player's next move based on past behavior.
    * **Logic**: Uses A* Search to plot an intercept path.
* **Medical Assistant**:
    * **ML**: Identifies potential anomalies in medical images.
    * **Logic**: Cross-references findings with clinical guidelines and patient history.
* **Smart Home**:
    * **ML**: Predicts when the user will arrive based on phone GPS patterns.
    * **Logic**: Optimizes thermostat schedule based on energy cost rules.

## Example: Robot Navigation

* **Approach**: Map LIDAR sensor vectors directly to steering actions using a learned model.
* **Advantage**: Learns complex geometric patterns (corners, dead ends) from demonstrations.

# Conclusion

## Summary
* **ML Agents** learn from experience $(E)$ to perform tasks $(T)$ better over time $(P)$.
* **Classical Models** (KNN, NB, Perceptron, Logistic, DT) offer different trade-offs in speed, interpretability, and complexity.
* **Limitations**: Overlap, Dimensionality, and Inductive Bias define the boundaries of what is learnable.
* **Hybrid Architectures** combine the perception of ML with the strategic reliability of Logic.
