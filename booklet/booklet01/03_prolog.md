# Prolog and Logic Programming

Prolog, short for *Programmation en Logique* (Programming in Logic), is the premier language of the logic programming paradigm. Unlike imperative languages that require a programmer to specify a sequence of steps to solve a problem, Prolog allows the developer to describe the problem itself as a set of facts and rules. The underlying engine then uses automated reasoning—specifically **Resolution** and **Unification**—to find answers to queries. This chapter explores the syntax, mechanics, and practical applications of Prolog in the design of intelligent agents.

## The Foundations of Prolog Syntax

Prolog programs are composed of three basic building blocks: **atoms**, **variables**, and **compound terms**. These elements are used to construct **facts** and **rules**, which together form the knowledge base.

*   **Atoms**: These are constants that represent specific objects or properties. They must begin with a lowercase letter (e.g., `apple`, `hall`) or be enclosed in single quotes if they contain spaces or start with uppercase (e.g., `'John Smith'`).
*   **Variables**: Variables are placeholders for terms and must begin with an uppercase letter or an underscore (e.g., `X`, `Result`, `_hidden`). The anonymous variable `_` is used when the value of a term is irrelevant.
*   **Facts**: A fact is a simple assertion that a relationship holds. For example, `parent(john, mary).` states that John is the parent of Mary.
*   **Rules**: A rule defines a relationship based on other relationships. It uses the "neck" operator `:-`, which represents logical implication ($\Leftarrow$). The general form is `Head :- Body.`, meaning "Head is true if Body is true."

**Example: The Family Tree**
```prolog
parent(john, mary).
parent(mary, alice).
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
```
In this snippet, `grandparent(X, Y)` is true if there exists some `Z` such that `X` is the parent of `Z` AND `Z` is the parent of `Y`.

## The Mechanics of Inference

When a user issues a **Query** (using the `?-` operator), Prolog attempts to prove the query by searching its knowledge base. This process involves two core mechanisms: **Unification** and **Backtracking**.

### Unification
Unification is the process of matching two terms by finding a **substitution** of variables that makes them identical. In Prolog, the `=` operator represents unification, not assignment.

**Equation of Unification**:
Two terms $T_1$ and $T_2$ unify if there exists a substitution $\theta$ such that:
$$T_1\theta = T_2\theta$$

**Example**: The query `?- foo(A, B) = foo(1, 2).` results in the substitution $\theta = \{A/1, B/2\}$.

### Backtracking and the SLD Tree
Prolog uses a **Depth-First Search (DFS)** strategy to explore the knowledge base. If it reaches a "dead end" (a goal that cannot be proved), it "backtracks" to the last choice point and attempts an alternative rule. This process can be visualized as an **SLD Tree** (Selective Linear Definite clause resolution).

\begin{center}
\begin{tikzpicture}[node distance=1.5cm, auto, thick, >=stealth]
    \node (root) {?-- grandparent(john, Y)};
    \node (c1) [below=of root, xshift=-2.5cm] {?-- parent(john, Z), parent(Z, Y)};
    \node (c2) [below=of c1, yshift=-0.5cm] {?-- parent(mary, Y) [Z=mary]};
    \node (leaf) [below=of c2, yshift=-0.5cm] {Y = alice};
    
    \draw[->] (root) -- node [left, font=\small] {Unify rule} (c1);
    \draw[->] (c1) -- node [left, font=\small] {Unify fact} (c2);
    \draw[->] (c2) -- node [left, font=\small] {Unify fact} (leaf);
\end{tikzpicture}
\end{center}

## List Processing and Recursion

Lists are the primary data structure in Prolog. A list is either empty (`[]`) or consists of a **Head** (the first element) and a **Tail** (the rest of the list). The notation `[H|T]` is used to deconstruct a list.

**Example: Counting Elements**
```prolog
count([], 0).
count([_|T], N) :- count(T, N1), N is N1 + 1.
```
This recursive rule states that the count of an empty list is 0, and the count of a non-empty list is $1$ plus the count of its tail.

Mathematically, a list $[a, b, c]$ is a nested structure:
$$.(a, .(b, .(c, [])))$$
where the dot (`.`) is the list constructor.

## Controlling Search: The Cut Operator (`!`)

Prolog's default backtracking behavior can sometimes lead to inefficiency or incorrect logic. The **Cut** operator (`!`) is used to "freeze" the current choices. Once a cut is encountered, Prolog commits to the current branch and will not backtrack past the cut for that specific goal.

**Example: Mutually Exclusive Rules**
```prolog
perceive_hint(Secret, Guess, hot) :- Guess > Secret, !.
perceive_hint(Secret, Guess, cold) :- Guess < Secret, !.
perceive_hint(Secret, Guess, found) :- Guess =:= Secret.
```
Here, if `Guess > Secret` is true, the cut prevents Prolog from even attempting the `cold` or `found` rules, saving computation time and ensuring only one hint is returned.

## Dynamic Knowledge Bases and Agent Memory

While traditional Prolog is static, intelligent agents often need to update their knowledge as they explore an environment. Prolog provides **dynamic predicates** for this purpose.

*   `:- dynamic predicate/arity.`: Declares that a predicate can be modified at runtime.
*   `assertz(Fact).`: Adds a new fact to the end of the KB.
*   `retract(Fact).`: Removes a fact from the KB.

**Example: Updating Agent Location**
```prolog
move(NewRoom) :-
    retract(location(agent, _)),
    assertz(location(agent, NewRoom)).
```
This simple rule allows an agent to "forget" its old location and "remember" a new one, effectively managing state within a declarative framework.

## Case Study: The Hot or Cold Agent

Consider an agent tasked with finding a secret number within a range. The environment provides feedback: "hot" if the guess is too high and "cold" if it is too low. The agent uses a binary search strategy implemented in Prolog.

\begin{center}
\begin{tikzpicture}[node distance=1.5cm, auto, thick, >=stealth]
    \node (start) [rectangle, draw, fill=gray!05] {Initial Guess (50)};
    \node (perceive) [below=of start] {Perception: "hot"};
    \node (act) [below=of perceive] {Update Max: 49};
    \node (next) [below=of act] {Next Guess (25)};
    
    \draw[->] (start) -- (perceive);
    \draw[->] (perceive) -- (act);
    \draw[->] (act) -- (next);
    \draw[->] (next.east) -- ++(1,0) |- node [pos=0.25, right, font=\small] {Loop} (perceive.east);
\end{tikzpicture}
\end{center}

The agent logic relies on the `is` operator for arithmetic evaluation and `//` for integer division. The core of the search is a recursive `solve` predicate that updates boundaries until the `found` condition is met.

## Integration: Prolog and Python

While Prolog excels at reasoning, other languages like Python are often preferred for data processing or user interfaces. The **PySwip** library allows for seamless integration, enabling Python programs to consult Prolog files and query the knowledge base as if it were a native data source. This hybrid approach—using Python for "muscles" and Prolog for the "brain"—is a powerful pattern for modern AI systems.
