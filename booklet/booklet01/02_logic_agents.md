# Logic-Based Agents

Logic-based agents represent a paradigm of artificial intelligence where reasoning is performed through the manipulation of symbolic representations. Unlike imperative systems that follow a fixed sequence of instructions, a logic-based agent operates declaratively: it maintains a **Knowledge Base (KB)** of facts and rules about the world and uses an **Inference Engine** to deduce what actions to take. This approach separates the "what" (the knowledge) from the "how" (the reasoning process), providing a transparent and mathematically rigorous framework for intelligent behavior.

## Architecture of a Knowledge-Based Agent

A knowledge-based agent is structured around its ability to internalize perceptions as logical sentences and query its knowledge for optimal responses. The fundamental loop of such an agent involves receiving a percept, translating it into the internal logic language, "telling" the KB about this new information, and then "asking" the KB for the best action to execute.

\begin{center}
\begin{tikzpicture}[node distance=2.5cm, auto, thick, >=stealth]
    \node (percept) [circle, draw, fill=blue!05] {Percept};
    \node (translate) [rectangle, draw, right=of percept, xshift=1cm] {Translator};
    \node (kb) [cylinder, draw, shape border rotate=90, right=of translate, xshift=1cm, minimum width=2cm, minimum height=2cm, fill=orange!05] {KB};
    \node (inference) [rectangle, draw, below=of kb, yshift=-0.5cm, rounded corners, minimum width=3cm, minimum height=1cm, fill=green!05] {Inference Engine};
    \node (actuator) [circle, draw, left=of inference, xshift=-2cm, fill=red!05] {Action};
    
    \draw[->] (percept) -- (translate);
    \draw[->] (translate) -- node {Tell} (kb);
    \draw[<->] (kb) -- node [right] {Ask} (inference);
    \draw[->] (inference) -- (actuator);
\end{tikzpicture}
\end{center}

The **Agent Function** is the abstract mapping from percept sequences to actions, $f: P^* \rightarrow A$. In a logic-based agent, this function is realized by the **Agent Program**, which implements the inference engine. This separation allows for **Declarative Programming**, where the developer describes the properties of the solution rather than the steps to reach it.

**Example**: In an imperative system, one might write `if wall_ahead: turn_left()`. In a declarative logic system, one defines the rule `Clear(ahead) \wedge \neg Wall(ahead) \implies CanMove(ahead)`. The agent then searches for a state where `CanMove(ahead)` is true to decide its next step.

## The Language of First-Order Logic (FOL)

To represent complex worlds, we require the expressive power of **First-Order Logic (FOL)**. While Propositional Logic deals with simple facts, FOL introduces objects, relations (predicates), and functions.

### Formal Syntax
The syntax of FOL is defined by a set of recursive rules, often represented in Backus-Naur Form (BNF). A formula can be an atomic formula, a combination of formulas using connectives ($\neg, \wedge, \vee, \Rightarrow, \Leftrightarrow$), or a quantified formula using $\forall$ (Universal) or $\exists$ (Existential).

$$
\begin{aligned}
\text{Term} &\to \text{Function}(\text{Term}, \dots) \mid \text{Constant} \mid \text{Variable} \\
\text{AtomicSentence} &\to \text{Predicate}(\text{Term}, \dots) \mid \text{Term} = \text{Term} \\
\text{Sentence} &\to \text{AtomicSentence} \mid (\text{Sentence} \text{ Connective } \text{Sentence}) \mid \text{Quantifier Variable Sentence}
\end{aligned}
$$

### Semantics: Interpretations and Models
The meaning of a formula is determined by an **Interpretation**, which maps symbols to entities in a domain (the "Universe"). A **Model** is an interpretation that satisfies a formula (makes it true).

**Example: The Blocks World**
Consider a domain $\{A, B, C, Floor\}$. We define the predicate $OnTop(x, y)$.
An interpretation might be: $OnTop(B, A) = True$, $OnTop(A, C) = True$, and $OnTop(C, Floor) = True$. This model represents a stack of three blocks ($B$ on $A$ on $C$) on the floor.

\begin{center}
\begin{tikzpicture}[thick]
    \draw (0,0) -- (4,0) node [right] {Floor};
    \draw (1,0) rectangle (2,1) node [pos=.5] {$C$};
    \draw (1,1) rectangle (2,2) node [pos=.5] {$A$};
    \draw (1,2) rectangle (2,3) node [pos=.5] {$B$};
\end{tikzpicture}
\end{center}

## Inference and Reasoning

Inference is the process of deriving new sentences from old ones. The most common rule is **Modus Ponens**:
$$\frac{P \Rightarrow Q, \quad P}{Q}$$
This rule is sound; if the premises are true, the conclusion is guaranteed to be true.

### Unification
In FOL, we often need to match a general rule to a specific fact. **Unification** is the process of finding a substitution $\theta$ that makes two logical expressions identical.
*   **Example**: Unifying $At(Agent, x)$ with $At(Agent, Kitchen)$ yields the substitution $\theta = \{x/Kitchen\}$.

### Resolution and Proof by Refutation
**Resolution** is a powerful inference rule that operates on clauses in Conjunctive Normal Form (CNF). A common technique is **Proof by Refutation**: to prove a goal $G$, we add $\neg G$ to the KB and attempt to derive a contradiction (the empty clause $\square$).

## Knowledge Representation Challenges

Representing a changing world introduces several technical hurdles, most notably the **Frame Problem**.

### The Frame Problem
When an agent performs an action, most facts about the world remain unchanged. However, in pure logic, we must explicitly state what *doesn't* change. If an agent moves a cup, the color of the walls remains the same, the temperature of the room remains the same, and the location of the floor remains the same. Listing every non-change for every action leads to a "combinatorial explosion" of axioms.

The solution is the use of **Successor-State Axioms**, which define the value of a property (a **Fluent**) at time $t+1$ based on the actions at time $t$:
$$F(t+1) \iff [\text{Action made } F \text{ true}] \vee [F(t) \wedge \neg (\text{Action made } F \text{ false})]$$

## Case Study: The Wumpus World

The Wumpus World is a classic environment for testing logic-based agents. It consists of a $4 \times 4$ grid containing pits, a gold treasure, and a monster (the Wumpus).

*   **Percepts**: The agent perceives a *Breeze* if adjacent to a pit, a *Stench* if adjacent to the Wumpus, and a *Glitter* if in the same square as the gold.
*   **Rules**: 
    $$\forall x,y\ Breeze(x,y) \Leftrightarrow \exists a,b\ Adj(x,y,a,b) \wedge Pit(a,b)$$
    $$\forall x,y\ Stench(x,y) \Leftrightarrow \exists a,b\ Adj(x,y,a,b) \wedge Wumpus(a,b)$$

By observing a breeze in $(1,1)$ and nothing in $(2,1)$, the agent can use resolution to deduce which adjacent cells are safe.

\begin{center}
\begin{tikzpicture}[scale=1.2]
    \draw (0,0) grid (4,4);
    \node at (0.5,0.5) {Agent};
    \node at (0.5,1.5) {Breeze};
    \node at (2.5,2.5) {Wumpus};
    \node at (1.5,3.5) {Pit};
    \node at (3.5,0.5) {Gold};
    
    \draw[thick, red] (2,2) -- (3,2) -- (3,3) -- (2,3) -- cycle;
    \node[red] at (2.5,3.2) {Stench Area};
\end{tikzpicture}
\end{center}

## Rule-Based Systems and Logic Programming

Logic-based agents often employ specific reasoning strategies:
*   **Forward Chaining**: Data-driven reasoning. It starts with known facts and applies rules to see what else can be deduced. This is useful for real-time monitoring.
*   **Backward Chaining**: Goal-driven reasoning. It starts with a goal and works backward through rules to find supporting facts. This is the strategy used by **Prolog**.

### Horn Clauses
To ensure efficient inference, many systems restrict themselves to **Horn Clauses**, which have at most one positive literal.
$$\neg P_1 \vee \neg P_2 \vee \dots \vee \neg P_n \vee Q \equiv (P_1 \wedge P_2 \wedge \dots \wedge P_n) \Rightarrow Q$$
In Prolog, this is written as `Q :- P1, P2, ..., Pn.` This restriction allows the inference engine to use **Depth-First Search (DFS)** with backtracking to explore potential proofs efficiently.

## Summary

Logic-based agents provide a rigorous foundation for AI. They are **symbolic**, meaning their knowledge is represented in human-readable forms; **transparent**, allowing the reasoning process to be inspected; and **rigorous**, providing mathematical guarantees about the correctness of their deductions. While they can be brittle in the face of uncertainty, they remain the backbone of expert systems, formal verification, and automated theorem proving.
