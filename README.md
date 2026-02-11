# Intelligent Systems II

![Course Banner](https://img.shields.io/badge/Course-Intelligent_Systems_II-blue.svg) ![Year](https://img.shields.io/badge/Year-2025%2F2026-green.svg)

## Course Overview

This repository contains the syllabus, lecture slides, and practice materials for **Intelligent Systems II**.
The course builds upon fundamental AI concepts to explore advanced agents, knowledge representation, semantic communication, and machine learning.

The curriculum focuses on designing agents that can perceive, reason, act, and learn within their environments.

## Repository Structure

The content is organized into the following directories:

* **`slides/`**: Contains the theoretical lecture notes and presentations.
* **`practice/`**: Contains practical exercises, code snippets (Prolog/Python), and lab guides.

## Topics Covered

### 1. Knowledge Representation & Logic
Refining the ability to represent the world symbolically.
* **Logic Revision:** Propositional Logic, First-Order Logic (FOL), Resolution, and Unification.
* **Prolog Programming:** Advanced logic programming, list processing, cut operator, and negation as failure.
* **Knowledge Integration:** Using **PySWIP** to bridge Python and Prolog.
* **Structured Knowledge:** Semantic Networks, Description Logics (DL), and the Semantic Web (OWL/Protegé).

### 2. Reasoning & Planning
How agents decide what to do next to achieve a goal.
* **Rule-Based Systems:** Forward Chaining (Data-driven) vs. Backward Chaining (Goal-driven).
* **Automated Planning:** STRIPS operators (Preconditions, Add/Delete lists), Linear planning, and "Blocks World" scenarios.

### 3. Natural Language Processing (NLP)
Enabling agents to communicate semantically with humans.
* **Communication:** Speech acts (KQML, FIPA-ACL) and agent protocols.
* **Grammars:** Definite Clause Grammars (DCG) in Prolog.
* **Parsing:** Handling number/gender agreement, sub-categorization, and generating logical forms from text.

### 4. Machine Learning
Moving from deductive reasoning to inductive learning.
* **Reinforcement Learning (RL):**
    * Markov Decision Processes (MDPs) & Bellman Equations.
    * Q-Learning and SARSA.
    * Deep Reinforcement Learning (DQN, Double DQN).
* **Inductive Logic Programming (ILP):** Learning relational rules from data (FOIL algorithm).
* **Explanation-Based Learning (EBL):** Generalizing from single examples using domain theory.

## Technologies & Tools

* **Languages:** Python, Prolog (SWI-Prolog).
* **Libraries:**
    * `PySWIP` (Python-Prolog bridge).
    * `Owlready2` (Ontology manipulation).
    * `Keras` / `PyTorch` / `TensorFlow` (For Deep RL).
* **Concepts:** Neural Networks, Genetic Algorithms, Resolution Theorem Proving.

## Evaluation

>TODO

## Bibliography

1.  **Russell, S., & Norvig, P.** (2021). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
2.  **Bratko, I.** (2012). *Prolog Programming for Artificial Intelligence* (4th ed.). Pearson.
3.  **Poole, D., & Mackworth, A.** *Artificial Intelligence: Foundations of Computational Agents*.

## Authors

* **Mário Antunes** - [mariolpantunes](https://github.com/mariolpantunes)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details