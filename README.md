# Artificial Intelligence Fundamentals (AIF) Project

![AI Logo](logo.jpeg)

## University of Pisa - First Year, First Semester

### Course Overview

Welcome to the Artificial Intelligence Fundamentals course project! This project is designed to provide hands-on experience with the core concepts and techniques in AI.

### Project Objectives

- **Understand** the basics of AI and state-of-the-art algorithms.
- **Implement** simple AI algorithms.
- **Analyze** the performance of different AI algorithms.
- **Collaborate** with peers to solve complex problems.

### Project Structure

### Project Title: **DareFightingICE AI Agent Development**

### Team Members: 
1. Person A - Project Lead & Game Strategy Design
2. Person B - AI Agent Programming & Search Techniques
3. Person C - Logic and Planning Specialist
4. Person D - Probabilistic Reasoning & Uncertainty Management
5. Person E - Multi-Agent Decision Making & Project Presentation

### Project Overview:
The goal of this project is to develop an AI agent capable of competing in the game **DareFightingICE**, a 1v1 fighting game where agents can utilize sound, video, and statistical inputs such as health points (HP), time, and damage. Unlike previous iterations of the competition that primarily focused on Reinforcement Learning (RL), this project will apply a diverse set of AI methods drawn from the **AIF course syllabus**. These techniques will include **search algorithms**, **logical reasoning**, **constraint satisfaction**, **automated planning**, **multi-agent decision making**, and **probabilistic reasoning**.

### Excluded Methods:
We will exclude **Reinforcement Learning** methods and instead emphasize alternative AI strategies like **adversarial search**, **first-order logic**, and **probabilistic reasoning**, making the project more aligned with classical AI techniques studied during the course.

---

### Project Structure:

#### 1. **Project Setup**
   - **Tools & Languages**: The project will use **Python** for AI agent development and **Java** for the game environment. The code will be based on the official DareFightingICE **repository**.
   - **Game Integration**: Integrate the game environment to allow the AI agent to interact with real-time game inputs such as sound, HP, and damage. Use both sound input data and other visual or statistical data for decision-making.
   - **Agent Control**: Develop functions to control the agent's movements, attacks, and defensive actions using strategic AI methods.

#### 2. **Search Algorithms and Adversarial Search**
   - **Adversarial Search**: Since DareFightingICE is a 1v1 game, we will implement **Minimax** and **Alpha-Beta Pruning** algorithms for the agent’s decision-making in adversarial settings. This will enable the agent to calculate the optimal moves while minimizing the opponent's success.
   - **Search in Complex Environments**: Apply **A* search** and other pathfinding algorithms to handle more complex movements and decisions, such as finding the shortest path to evade attacks or close the distance for offensive maneuvers.

#### 3. **Constraint Satisfaction Problems (CSP)**
   - **CSP Implementation**: The agent will face constraints such as limited time, available health, and possible damage. Implement **constraint satisfaction problems** to manage these limitations and optimize the agent's decision-making in real-time scenarios.
   - **Example**: Create constraints where the agent must balance attacking while conserving health and time, ensuring it doesn't run out of HP or miss critical timing windows in the game.

#### 4. **Logical Agents and First-Order Logic**
   - **Logical Reasoning**: Implement a **logical agent** using **first-order logic** to interpret game states and make intelligent decisions. For example, the agent could deduce when to switch from offense to defense based on available health points and opponent behavior.
   - **Inference Systems**: Use **inference** to predict the opponent’s actions based on their movement patterns, giving the agent an edge in planning its next move.

#### 5. **Automated Planning**
   - **Action Sequences**: The agent will need to plan sequences of actions (e.g., punch, kick, block) in advance. Use **automated planning** techniques to design the best sequence of moves given the opponent’s position and current HP.
   - **Real-Time Planning**: The game environment is dynamic, so the agent will continuously update its plans based on changing inputs such as remaining health and game time.

#### 6. **Probabilistic Reasoning and Uncertainty Management**
   - **Handling Uncertainty**: The agent will rely on **probabilistic reasoning** to handle uncertainty, especially when relying on sound inputs or incomplete visual information. For example, if the opponent’s position is uncertain, the agent will use probabilities to decide whether to engage or defend.
   - **Bayesian Networks**: Implement **Bayesian reasoning** to allow the agent to make informed decisions based on the likelihood of future events, such as predicting the opponent’s next move based on historical behavior.

#### 7. **Multi-Agent Decision Making**
   - **Opponent Modeling**: Develop strategies for **multi-agent decision making**, focusing on how the AI agent interacts with the bot agent or an opponent in the game. The AI will adapt to the opponent’s behavior and dynamically update its strategy using decision-making models.
   - **Dynamic Adjustment**: The agent will continuously adapt its strategy based on observed actions of the opponent, ensuring it remains competitive in the evolving game environment.

#### 8. **Project Presentation & Testing**
   - **Testing & Evaluation**: The AI agent will be rigorously tested against different bots and human players to evaluate performance. Metrics such as win rate, average damage dealt, and time efficiency will be used to refine the agent's decision-making process.
   - **Final Presentation**: Present the completed project during the final **Projects Presentation** session, showcasing the AI agent’s strategy and explaining the applied techniques. Emphasis will be placed on explaining how various AI methods were integrated into the final agent.

---

### Task Distribution:
Each team member will be responsible for a key aspect of the project:

1. **Person A (Project Lead)**: Manage overall project coordination, integration of components, and testing.
2. **Person B (AI Agent Programming)**: Develop and implement the agent’s control functions, search algorithms, and adversarial strategies.
3. **Person C (Logic and Planning)**: Focus on logical reasoning, constraint satisfaction, and automated planning for action sequences.
4. **Person D (Probabilistic Reasoning & Uncertainty Management)**: Implement probabilistic reasoning techniques for decision-making under uncertainty.
5. **Person E (Multi-Agent Decision Making & Presentation)**: Work on multi-agent decision-making strategies and prepare the final project presentation.

---

### Conclusion:
This project will create an AI agent capable of performing in the 1v1 DareFightingICE game environment. The agent will not rely on Reinforcement Learning but instead use classical AI techniques, including **adversarial search**, **constraint satisfaction**, **logical reasoning**, **automated planning**, and **probabilistic reasoning**. Each technique will contribute to a robust and competitive AI capable of dynamic decision-making in a highly adversarial setting.

### Tools and Technologies

- **Programming Languages:** Python
- **Libraries:** To define
- **Platforms:** Jupyter Notebook, Google Colab

### Evaluation Criteria

- **Code Quality:** Clean, well-documented code.
- **Innovation:** Creative and effective solutions.
- **Collaboration:** Effective teamwork and communication.
- **Presentation:** Clear and concise project presentation.

### Resources

- [Course Syllabus](https://elearning.di.unipi.it/course/view.php?id=1003)
- [Project Guidelines](https://elearning.di.unipi.it/pluginfile.php/84167/mod_resource/content/4/03_projects_proposals.pdf)

---

> "The future belongs to those who learn more skills and combine them in creative ways." - Robert Greene

![University of Pisa](unipi.png)
