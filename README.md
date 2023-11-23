## Before started

This project is primarily for **educational purposes** and **will not be further developed or maintained**. You are free to copy and modify it based on your use case. However, I would appreciate it if you or your team **find inspiration** from the project, and succesfully apply it in Robocon, **share among peers**, **mention it in boardcaster interviews**, and **give the repository a star**. Please note that this repository **does not guarantee your success** in ABU Robocon 2024. It serves as a reinforcement learning kick-start project, and it is essential for your team to **enhance the code and adapt it to your specific use case**. I hope this project can assist you and your team, and I wish you the **best of luck and enjoyment with Robocon 2024 Harvest Day**.

Written and Coded by **ABU Robocon 2019 Grand Prix Programmer** from the Team at The Chinese University of Hong Kong in 2019.

----
# Robocon 2024 Harvest Day - Silo Game Reinforcement Learning

This project is a virtual Robocon 2024 Silo Game Reinforcement Learning implementation using the Q-values algorithm. It is written in Python 3 and focuses specifically on the Robocon 2024 Harvest Day Area 3 Silo Game Task. I hope it can serve as a solid starting point for you to delve into the world of Deep Learning with reinforcement learning, as it is the first autonomous decision-making game.

python3 version: 3.7.9

## Installation
The installation process is simple and does not require any advanced deep learning libraries. It aims to help you gain a better understanding of how Reinforcement Learning works.
```bash
pip install -r requirements.txt
```

## Usage

To train models, use the following command:
```bash
python robocon2024.py train
```

To play a game, use the following command:
```bash
python robocon2024.py play --r 0 --b 0
```
Where 0 = AI, 1 = Player

An advance playing will be like the following
```bash
python .\robocon2024.py play --r 0  --rs 2 --rf 0 --rr 0.9 --b 0 --bs 2 --bf 0 --br 0.8
```
--r: Red player, where 0 = AI and 1 = Player
--b: Blue player, where 0 = AI and 1 = Player
--[color]s: The speed of the player of that color, representing the time taken to place one paddy rice into the silo.
--[color]f: The freeze time for the player of that color, which is the time when the robot starts in zone 3. The time before entering zone 3 is considered the freeze time.
--[color]r: The success rate of the player of that color, representing the rate at which the robot successfully places the paddy rice into the silo. Mechanical issues may lead to unsuccessful attempts.

There are more arguments available. For more information, refer to the following commands:
```bash
python robocon2024.py train -h
```

```bash
python robocon2024.py play -h
```
## Code Content
- player.py: This file includes three classes: Player (an abstract class), HumanPlayer (for manual input control), and AIPlayer (for trained players).
- robocon2024.py: This is the main program where the entire game flow starts.
- silo.py: This file contains the Silo object, representing a 3x5 silo. Silo is the main object, and VirtualSilo is used for virtual players to play against.

## Self-understanding in Q-value reinforcement learning
You can easily find more information about Q-value reinforcement learning online. Personally, I don't like the formula as I have no idea about it. In short, there are states and actions. We use a table with columns representing states and rows representing actions. The table contains values, which represent the reward of taking a specific action in a particular state. We can determine the action based on the state that provides the maximum reward. Initially, we don't know the values for states and actions. However, we can run a training process by simulating games and recording the decisions based on random actions. From the results, we can assess whether the agent (the model) wins or not and assign a reward accordingly. The reward can be positive or negative, and we update the tables accordingly. By running a large number of games, the tables of states and actions should converge, and given a state, we can determine which action will yield the highest score.

## Follow up
I am open to discussions and happy to answer any questions. I also encourage you to visit the team at The Chinese University of Hong Kong for idea exchange. You can reach out to the team through [Instagram](https://www.instagram.com/cuhkrobocon/) or [Facebook](https://www.facebook.com/powershuttlecuhk).  Here are some hints for further development with this project:
1. Deep Reinforcement Learning
2. More parameters in training
