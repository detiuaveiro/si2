# Foundations of Logic

Logic is the cornerstone of formal reasoning, providing the mathematical framework necessary to represent knowledge and derive new information from existing facts. At its core, logic allows us to abstract away from the physical world and operate within a symbolic system where truths can be calculated with precision. In the context of computer science and artificial intelligence, logic systems are the engines that power automated reasoning, rule-based systems, and formal verification.

## Prelude: The Boolean Perspective

Before exploring complex symbolic systems, it is instructive to consider the most fundamental form of logic: Boolean logic. Named after George Boole, this system operates on two states—typically denoted as $1$ (True, On, or High) and $0$ (False, Off, or Low). Boolean logic is the foundation of digital circuitry, where physical switches represent logical variables.

Consider a simple electrical circuit involving two switches, $A$ and $B$, connected in series to a lamp $L$. The lamp will only illuminate if both switches are closed. This physical arrangement is a direct implementation of the logical **AND** ($\wedge$) operation.

\begin{center}
\begin{tikzpicture}[thick, scale=1.2]
  % Power source (simplified)
  \draw (0,0) -- (0,0.8);
  \draw (-0.3,0.8) -- (0.3,0.8);
  \draw (-0.15,0.9) -- (0.15,0.9);
  \draw (-0.3,1.0) -- (0.3,1.0);
  \draw (-0.15,1.1) -- (0.15,1.1);
  \draw (0,1.1) -- (0,2) -- (1,2);
  
  % Switch A
  \draw (1,2) -- (1.4,2.4) node[above] {$A$};
  \draw (1.5,2) -- (2,2);
  
  % Switch B
  \draw (2,2) -- (2.4,2.4) node[above] {$B$};
  \draw (2.5,2) -- (3.5,2);
  
  % Lamp L
  \draw (3.75,2) circle (0.25);
  \draw (3.57,1.82) -- (3.93,2.18);
  \draw (3.57,2.18) -- (3.93,1.82);
  \node at (3.75,2.5) {$L$};
  
  \draw (4,2) -- (5,2) -- (5,0) -- (0,0);
\end{tikzpicture}
\end{center}

Mathematically, we represent the state of the lamp as a function of the switches:
$$L = A \wedge B$$

This relationship is fully described by a **truth table**, which enumerates every possible combination of inputs and the resulting output:

| Switch $A$ | Switch $B$ | Lamp ($L$) |
| :---: | :---: | :---: |
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| **1** | **1** | **1** |

The power of this abstraction is that it allows us to predict the state of the lamp without physical observation. If we know that $A$ is True and $B$ is True, logic dictates that $L$ must be True.

## The Architecture of a Logic System

A formal logic system is not merely a set of symbols; it is a structured environment composed of three essential pillars:

1.  **Syntax**: This defines the "grammar" of the system. It specifies the alphabet of symbols and the rules for combining them into **Well-Formed Formulas (WFF)**. Syntax determines what is *legal* to write, regardless of whether it is true or false.
2.  **Semantics**: This provides the "meaning" of the formulas. It establishes a mapping between the symbolic expressions and the domain of discourse (the "real world"). In propositional logic, for instance, semantics are often defined using truth tables that assign truth values to variables.
3.  **Inference Rules**: These are the algorithms or procedural rules that allow for the derivation of new formulas from existing ones. An inference rule is a transformation that preserves truth; if the starting formulas are true, the derived formulas must also be true.

\begin{center}
\begin{tikzpicture}[node distance=2.5cm, auto, >=stealth]
    \node (kb) [rectangle, draw, minimum width=3cm, minimum height=1cm, fill=blue!05] {Knowledge Base ($KB$)};
    \node (inf) [rectangle, draw, rounded corners, right=of kb, xshift=1.5cm, minimum width=3cm, minimum height=1cm, fill=orange!05] {Inference Engine};
    \node (out) [rectangle, draw, right=of inf, xshift=1.5cm, minimum width=3cm, minimum height=1cm, fill=green!05] {New Knowledge ($\alpha$)};
    
    \draw[->] (kb) -- node {Sentences} (inf);
    \draw[->] (inf) -- node {Proof Rules} (out);
    
    \node (sem) [below=of inf, yshift=0.5cm, font=\small\itshape] {Semantics (Interpretation)};
    \draw[dashed, <->] (inf) -- (sem);
\end{tikzpicture}
\end{center}

## Propositional Logic

Propositional logic is the simplest branch of formal logic. It deals with **propositions**, which are declarative statements that are either True or False. For example, "The sky is blue" is a proposition, whereas "Close the door!" is not.

In this system, we use **propositional variables** (such as $P, Q, R$) to represent these statements. These variables are then combined using **logical connectives**:

*   **Negation ($\neg$)**: "Not $P$". Flips the truth value.
*   **Conjunction ($\wedge$)**: "$P$ and $Q$". True only if both are true.
*   **Disjunction ($\vee$)**: "$P$ or $Q$". True if at least one is true.
*   **Implication ($\Rightarrow$)**: "If $P$, then $Q$". This is a causal or conditional link. It is only false if $P$ is true and $Q$ is false.
*   **Biconditional ($\Leftrightarrow$)**: "$P$ if and only if $Q$". True if both have the same truth value.

**Example**:
Let $P$ represent "It is raining" and $Q$ represent "The ground is wet". The formula $P \Rightarrow Q$ formalizes the rule that rain implies a wet ground. If we observe $P$ (it is raining), we can infer $Q$ (the ground is wet).

## First-Order Logic (FOL)

While propositional logic is powerful, it is limited by its inability to describe individual objects or the relationships between them. It treats every statement as an indivisible unit. **First-Order Logic (FOL)**, also known as Predicate Logic, extends this by introducing a more granular vocabulary:

*   **Objects (Constants)**: Represent specific entities in the world, such as `Alice`, `Aveiro`, or the number `5`.
*   **Functions**: Mappings that take one or more objects and return another object. For instance, $FatherOf(Bob)$ returns the object representing Bob's father.
*   **Predicates (Relations)**: Mappings that take objects and return a truth value. For example, $Greater(5, 3)$ is True, while $Near(Lisbon, Oporto)$ might be False.
*   **Variables**: Placeholders (like $x, y$) that can stand for any object in the domain.

### Quantifiers

FOL introduces **quantifiers** to express statements about sets of objects:

1.  **Universal Quantifier ($\forall$)**: Indicates that a property holds for **all** objects in the domain.
    *   *Example*: "All humans are mortal" $\rightarrow \forall x (Human(x) \Rightarrow Mortal(x))$.
    *   *Note*: A common pitfall is using $\wedge$ with $\forall$. $\forall x (Human(x) \wedge Mortal(x))$ would mean "Everything in the universe is both human and mortal."

2.  **Existential Quantifier ($\exists$)**: Indicates that there is **at least one** object in the domain for which the property holds.
    *   *Example*: "Some bird cannot fly" $\rightarrow \exists x (Bird(x) \wedge \neg CanFly(x))$.
    *   *Note*: Using $\Rightarrow$ with $\exists$ is usually a mistake. $\exists x (Bird(x) \Rightarrow \neg CanFly(x))$ is vacuously true if there exists anything in the universe that is *not* a bird.

## Interpretations, Models, and Entailment

The relationship between syntax and the world is defined by an **Interpretation**. 
*   In Propositional Logic, an interpretation is simply an assignment of True/False to every variable.
*   In FOL, it is a complex mapping of constant symbols to objects, predicate symbols to relations, and function symbols to functional mappings within a specific domain.

A **Model** is an interpretation in which a given formula evaluates to True. We say a formula is **Satisfiable** if it has at least one model. If a formula is True in *every* possible interpretation, it is a **Tautology** or is **Valid**.

**Entailment ($\models$)** is the fundamental relationship in logic. We say that a Knowledge Base ($KB$) entails a sentence $\alpha$ ($KB \models \alpha$) if and only if in every model where $KB$ is true, $\alpha$ is also true. This is the goal of reasoning: to find what else must be true given what we already know.

## Rewrite Rules and Normal Forms

Logic allows for algebraic manipulation through **Equivalences**. These are rules that allow us to transform formulas while preserving their truth value.

### Key Equivalences
*   **De Morgan's Laws**: 
    $$\neg (A \wedge B) \equiv \neg A \vee \neg B$$
    $$\neg (A \vee B) \equiv \neg A \wedge \neg B$$
*   **Implication Elimination**: 
    $$(A \Rightarrow B) \equiv (\neg A \vee B)$$
*   **Quantifier Duality**: 
    $$\neg \forall x P(x) \equiv \exists x \neg P(x)$$
    $$\neg \exists x P(x) \equiv \forall x \neg P(x)$$

### Conjunctive Normal Form (CNF)

For automated reasoning, it is often necessary to convert formulas into a standardized format called **Conjunctive Normal Form (CNF)**. A formula in CNF is a conjunction ($\wedge$) of one or more **clauses**, where each clause is a disjunction ($\vee$) of **literals** (atoms or negated atoms).

**Example**:
The formula $(A \vee B) \wedge (\neg B \vee C \vee D) \wedge (\neg A)$ is in CNF. This format is essential for the Resolution algorithm.

## The Resolution Inference Rule

Resolution is a powerful and computationally efficient inference rule that serves as the backbone of many automated theorem provers. It operates on clauses in CNF and generalizes the classical *Modus Ponens*.

### Propositional Resolution

The rule states that if we have two clauses where one contains a literal $P$ and the other contains its negation $\neg P$, we can "resolve" them to produce a new clause containing all other literals from both:

$$\frac{A \vee B, \quad \neg B \vee C}{A \vee C}$$

**Logic**: If $B$ is false, then $A$ must be true (from the first clause). If $B$ is true, then $C$ must be true (from the second clause). Since $B$ must be either true or false, it follows that $A \vee C$ must be true.

### Unification

In FOL, literals often contain variables. To resolve them, we must first make them identical through **Unification**. This involves finding a **substitution** $\theta$ (a mapping of variables to terms) that makes two expressions match.

**Example**:
To unify $Knows(John, x)$ and $Knows(y, Mother(y))$, we apply the substitution $\theta = \{y/John, x/Mother(John)\}$, resulting in the unified atom $Knows(John, Mother(John))$.

### Proof by Refutation

Resolution is typically used in a **Proof by Refutation** ($Reductio\ ad\ Absurdum$). To prove that $KB \models \alpha$, we:
1.  Assume the negation of the goal: $\neg \alpha$.
2.  Add $\neg \alpha$ to the $KB$.
3.  Convert the entire set to CNF.
4.  Repeatedly apply Resolution.
5.  If we derive the **Empty Clause** ($\square$), which represents a contradiction ($False$), then the original goal $\alpha$ must be a logical consequence of $KB$.

\begin{center}
\begin{tikzpicture}[node distance=2cm, thick, >=stealth]
    \node (c1) {$A \vee B$};
    \node (c2) [right=of c1, xshift=2cm] {$\neg B \vee C$};
    \node (c3) [right=of c2, xshift=1.5cm] {$\neg A$};
    
    \node (res1) [below=of c1, xshift=1.75cm, yshift=-0.5cm, draw, rounded corners, fill=gray!05] {$A \vee C$};
    \node (res2) [below=of res1, xshift=1.25cm, yshift=-0.5cm, draw, circle, fill=gray!10] {$C$};
    
    \draw[->] (c1.south) -- (res1.north);
    \draw[->] (c2.south) -- (res1.north);
    \draw[->] (res1.south) -- (res2.north);
    \draw[->] (c3.south) -- (res2.north);
\end{tikzpicture}
\end{center}

## Horn Clauses and Logic Programming

In many practical applications, we restrict the logic to a subset called **Horn Clauses**. A Horn Clause is a clause with **at most one positive literal**. This restriction allows for much faster inference, which is the basis for the **Prolog** programming language.

Horn clauses come in three flavors:
1.  **Rules**: $\neg P_1 \vee \dots \vee \neg P_n \vee H$, equivalent to $(P_1 \wedge \dots \wedge P_n) \Rightarrow H$. In Prolog: `H :- P1, ..., Pn.`
2.  **Facts**: A single positive literal $H$. In Prolog: `H.`
3.  **Goals**: A clause with no positive literals $\neg G_1 \vee \dots \vee \neg G_n$. In Prolog: `:- G1, ..., Gn.`

Systems using Horn clauses can employ **Forward Chaining** (starting from facts to reach a conclusion) or **Backward Chaining** (starting from a goal and working back to facts), making them highly efficient for expert systems and automated reasoning.
