# Artificial Intelligence Fundamentals (AIF) Project

![AI Logo](logo.jpeg)

## University of Pisa - First Year, First Semester

### Course Overview

Welcome to the Artificial Intelligence Fundamentals course project! This project is designed to provide hands-on experience with the core concepts and techniques in AI.

### How to try the game

The latest Dare Fighting ICE (v7.0beta) files were downloaded from [here](https://github.com/TeamFightingICE/FightingICE/releases).

To try the game, you can run the following command inside DareFightingICE-7.0beta folder:

Windows
```bash
java -cp FightingICE.jar;./lib/*;./lib/lwjgl/*;./lib/lwjgl/natives/windows/amd64/*;./lib/grpc/*; Main --limithp 400 400 --grey-bg
```

Ubuntu:
```bash
java -cp FightingICE.jar:./lib/*:./lib/lwjgl/*:./lib/lwjgl/natives/linux/amd64/*:./lib/grpc/* Main --limithp 400 400 --grey-bg
```

MacOS:
```bash
java -XstartOnFirstThread -cp FightingICE.jar:./lib/*:./lib/lwjgl/*:./lib/lwjgl/natives/macos/arm64/*:./lib/grpc/* Main --limithp 400 400 --grey-bg
```

Should pop up this window: 

![Main Window](assets/main_window.png)

In this game `z` has the same effect as `enter`.
Hit `z` to start the game.

You should see the following screen:

![Character Selection](assets/screen-1.png)

- Move the `up` and `down` arrows to select the menu sub-items.
- Move the `left` and `right` arrows to select the player/character you want to play with.
- In my case, External AI gave null point exception, due to absence of the necessary files.
- I selected for Player 1: Keyboard and Player 2: MctsAi23i (which is a Monte Carlo Tree Search AI, I had already implemented).
- Move back to `PLAY` and hit `z` to start the game.

![Game Screen](assets/screen-2.png)

### Python Integration

Now we need to integrate the Python code with the game. To do this, we need to:

- Create a virtual environment with a specific python version. I use `conda` for this purpose.

```bash
conda create -n AIF python=3.12
```

- Activate the environment

```bash
conda activate AIF
```

- Next, we need to install all the required packages in `requirements.txt` file, which are: 
```python
pyftg==2.3b0
typer~=0.12.2
typing_extensions~=4.8.0
```
with the command:
```bash
pip install -r requirements.txt
```

Now we are all set to integrate the Python code with the game.

### Example of Python Integration

Refer to [this](https://github.com/TeamFightingICE/pyftg/tree/master/examples) repository for more information.

In the `example` folder, We have:

- `DisplayInfo.py` which is an example of AI that utilizes screen data as input.
- `KickAI.py` which is an example of AI that utilize a single command.
- `Main_PyAIvsPyAI.py` which is an example of AI vs AI game setting. Both implementation are in Python.

```python
async def start_process(
    host: str, port: int, character: str = "ZEN", game_num: int = 1
):
    gateway = Gateway(host, port)
    agent1 = KickAI()
    agent2 = DisplayInfo()
    gateway.register_ai("KickAI", agent1)
    gateway.register_ai("DisplayInfo", agent2)
    await gateway.run_game([character, character], ["KickAI", "DisplayInfo"], game_num)
```

This function, in the `Main_PyAIvsPyAI.py` creates two agents and runs the game. Therefore, if we want to implement our agent, we should follow their structure (e.g. `KickAI.py`)

Now we need to start the game, in one terminal (cmd):
Go to the `DareFightingICE-7.0beta` folder and run:

- Ubuntu:
```bash
java -cp FightingICE.jar:./lib/*:./lib/lwjgl/*:./lib/lwjgl/natives/linux/amd64/*:./lib/grpc/* Main --limithp 400 400 --grey-bg --pyftg-mode
```
- Windows:
```bash
java -cp FightingICE.jar;./lib/*;./lib/lwjgl/*;./lib/lwjgl/natives/windows/amd64/*;./lib/grpc/*; Main --limithp 400 400 --grey-bg --pyftg-mode 
```
- MacOS:
```bash
java -XstartOnFirstThread -cp FightingICE.jar:./lib/*:./lib/lwjgl/*:./lib/lwjgl/natives/macos/arm64/*:./lib/grpc/* Main --limithp 400 400 --grey-bg --pyftg-mode
```

You should see the following screen:

![Game Screen](assets/screen-3.png)

with terminal output:

```bash
Nov 19, 2024 3:57:58 PM manager.InputManager <init>
INFO: Create instance: manager.InputManager
Nov 19, 2024 3:57:58 PM manager.DisplayManager initialize
INFO: Create Window 960x640
Nov 19, 2024 3:57:59 PM manager.GraphicManager <init>
INFO: Create instance: manager.GraphicManager
Nov 19, 2024 3:57:59 PM loader.ResourceLoader <init>
INFO: Create instance: loader.ResourceLoader
Nov 19, 2024 3:57:59 PM core.Game initialize
INFO: Socket server is started, listening on 31415
Nov 19, 2024 3:57:59 PM gamescene.Socket initialize
INFO: Waiting to launch a game
```

which means the game is ready to start and waits on port `31415` for the python agents indication.

Next, we need to run the python code in another terminal (cmd). In the `example` folder, run:

```bash
python example/Main_PyAIvsPyAI.py --port 31414 --keyboard
```
`keyboard` is used so that we can control one of the agent with the keyboard. The other will be controlled by the code  in `DisplayInfo.py`.

You should see the following screen:

![Game Screen](assets/screen-4.png)

### Project Objectives

- **Understand** the basics of AI and state-of-the-art algorithms.
- **Implement** simple AI algorithms.
- **Analyze** the performance of different AI algorithms.
- **Collaborate** with peers to solve complex problems.

### Project Structure

### Project Title: **DareFightingICE AI Agent Development**

### Project Overview:
The goal of this project is to develop an AI agent capable of competing in the game **DareFightingICE**, a 1v1 fighting game where agents can utilize statistical inputs such as health points (HP), time, and damage. Unlike previous iterations of the competition that primarily focused on Reinforcement Learning (RL), this project will apply a diverse set of AI methods drawn from the **AIF course syllabus**. These techniques will include **search algorithms**, **logical reasoning**, **constraint satisfaction**, **automated planning**, **multi-agent decision making**, and **probabilistic reasoning**.

### Excluded Methods:
We will exclude **Reinforcement Learning** methods and instead emphasize alternative AI strategies like **adversarial search**, **first-order logic**, and **probabilistic reasoning**, making the project more aligned with classical AI techniques studied during the course.

---

## AI Agents

We have developed three distinct AI-based approaches for the DareFightingICE environment:

### 1. Prolog Agent Simo
A logic-based agent that uses Prolog for strategic decision making:
- Implements game logic rules in Prolog for decision making
- Uses knowledge base for state representation and tactical reasoning 
- Makes decisions based on current game state, opponent position, and HP/energy levels
- Leverages Prolog's pattern matching for move selection
- Handles basic combat moves and special attacks through logical inference

### 2. Problog Agent Ole
A probabilistic logic agent implemented using ProbLog:
- Uses probabilistic logic programming for decision making under uncertainty
- Implements probabilistic reasoning about opponent behavior and action outcomes
- Maintains dynamic probabilistic models of game state
- Makes decisions based on utility and probability scores
- Adapts strategy based on health, energy, and positional factors

### 3. Monte Carlo Tree Search (MctsAi) 
A search-based agent implementing Monte Carlo Tree Search:
- Uses MCTS for planning optimal move sequences
- Implements tree search with exploration vs exploitation balancing
- Simulates possible game states through rollouts
- Uses UCT formula for node selection
- Adapts search depth based on available computation time

Each agent demonstrates different AI techniques covered in the course:
- Logic programming and knowledge representation (Prolog Agent)
- Probabilistic reasoning and uncertainty (Problog Agent) 
- Tree search and planning (MCTS Agent)

## Project Files Overview

### Prolog Agent Implementation
- `prolog_based/prolog_agent_simo/PrologAI.py`: Main Prolog agent implementation using pyswip for Prolog integration
- `prolog_based/prolog_agent_simo/kb.pl`: Prolog knowledge base containing rules for strategic decision making

### Problog Agent Implementation
- `prolog_based/problog_agent_ole/ProblogAgent.py`: Main Problog agent using probabilistic logic programming
- `prolog_based/problog_agent_ole/terms.py`: Defines terms and predicates for probabilistic reasoning
- `prolog_based/problog_agent_ole/KB_V1.pl`: ProbLog knowledge base with probabilistic rules

### Monte Carlo Tree Search Implementation
- `monte_carlo_tree_search/MctsAi.py`: Main MCTS agent implementation
- `monte_carlo_tree_search/FighterState.py`: State representation and action handling for MCTS

### Shell Scripts and Automation
- `run_prolog_agent.sh`: Bash script for running the Prolog agent against the game environment
- `run_py_ag_parallel.sh`: Script for running multiple Python agents in parallel with configurable executions
- `monitor_restart.sh`: Monitoring script that watches for file changes and automatically restarts agents
- `common.sh`: Common utilities and functions shared between shell scripts

### Testing and Evaluation
- `stats_k=*/`: Directory containing test results and statistics for ProbLog agent
- `results_k=*.ipynb`: Jupyter notebooks for analyzing and visualizing Problog agent performance

### Documentation
- `README.md`: Project documentation and setup instructions
- `run_py_ag.md`: Instructions for running Python agents against the game environment
- `monitor_restart.md`: Guide for monitoring and restarting agents on file changes



### Tools and Technologies

- **Programming Languages:** Python
- **Libraries:** found in `requirements.txt` 
- **Platforms:** GitHub

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
