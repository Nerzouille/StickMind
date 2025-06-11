# Stick-IA

Implementation of an AI agent trained with Deep Q-Learning (DQN) to play the Stick Hero game autonomously.

## The Project:

Recreation of the popular mobile game "Stick Hero" with an intelligent agent capable of learning and mastering the game through reinforcement learning techniques.

This project focuses on implementing Deep Q-Learning algorithms to train an AI that can precisely calculate stick lengths to successfully navigate between platforms, demonstrating the application of machine learning in game environments.

## Features

- **Intelligent AI Agent**: DQN-based agent that learns optimal stick placement strategies
- **Multiple Difficulty Levels**: Easy, Normal, and Hard modes with adaptive platform sizes and gaps
- **Real-time Learning**: Watch the AI improve its performance during training
- **Visual Interface**: Beautiful Pygame-based graphics with smooth animations
- **Comprehensive Training System**: Complete training pipeline with model saving/loading
- **Performance Analytics**: Detailed metrics and success rate tracking
- **Interactive Controls**: Pause, resume, and manual override capabilities

## Installation

```bash
Downloads> git clone <repository_url>
...
Downloads/Stick-IA> pip install -r requirements.txt
...
```

## Usage/Examples

### Training a new AI agent:
```bash
Stick-IA> python train_ai.py
    🎮 Stick Hero IA - Training

    1. Train a new agent
    2. Test an existing agent

    Choice: 1
    Number of episodes [1000]: 1500

    🤖 Training started...
```

### Making the AI play:
```bash
Stick-IA> python play_game.py
    🤖 AI Stick Hero

    1. 🤖 Watch AI play
    2. 🎮 Play manually

    Choice: 1

    Available models:
    1. dqn_stick_hero_1500ep.pth (1500 episodes, 85% success)

    Model: 1
    Difficulty [normal]: hard
    Number of games [3]: 5

    🎮 AI plays 5 games
    ━━━ Game 1/5 ━━━
    🎯 Placement! Stick: 156 | Zone: 150-180 | Precision: 89% | SUCCESS
    🎉 SUCCESS - Score: 7
```

### Manual gameplay:
```bash
Stick-IA> python play_game.py
    Choice: 2

    🎮 Manual Stick Hero
    Controls: SPACE=Grow/Release stick, ESC=Quit
    Difficulty: normal
```

## Architecture

The AI system uses:
- **Deep Q-Network (DQN)** for decision making and learning
- **Experience Replay** for stable training and improved sample efficiency
- **Epsilon-greedy exploration** with adaptive decay for balanced exploration/exploitation
- **PyTorch** as the deep learning framework
- **Pygame** for game environment and visualization
- **Modular design** with separate environments for training and visual gameplay

## Game Mechanics

| Element | Description |
|---------|-------------|
| **Objective** | Grow stick to exact length needed to reach next platform |
| **Controls** | Grow stick (action 0) and Place stick (action 1) |
| **Scoring** | +1 for each successful platform reached |
| **Failure** | Stick too short (falls in gap) or too long (overshoots platform) |
| **Precision** | Bonus points for hitting optimal stick length |
| **Difficulty** | Progressive increase in gap distances and smaller platforms |

## AI State Space

The AI observes a 6-dimensional state vector:
- Gap distance to next platform
- Next platform width
- Current stick length
- Minimum stick length for success
- Maximum stick length for success
- Perfect stick length (center of platform)

## Supported Actions

| Action | Description | AI Logic |
|--------|-------------|----------|
| **0 - Grow** | Increase stick length | Continue growing when stick is too short |
| **1 - Place** | Stop growing and place stick | Place when stick reaches optimal length |

## Training Results

### Performance by Difficulty Level

|**Difficulty**|**Platform Size**|**Gap Range**|**AI Success Rate**|**Training Episodes**|
|--------------|-----------------|-------------|-------------------|-------------------|
|Easy|60-120px|100-200px|**95%**|1000|
|Normal|40-90px|120-250px|**85%**|1500|
|Hard|30-80px|150-300px|**72%**|2000|

### Learning Progression

```
Episode    100: Success Rate: 15% | Avg Score: 0.8
Episode    500: Success Rate: 45% | Avg Score: 2.1
Episode   1000: Success Rate: 75% | Avg Score: 4.3
Episode   1500: Success Rate: 85% | Avg Score: 6.7
```

## Technical Implementation

## File Structure

```
Stick-IA/
├── agents/
│   └── dqn_agent.py          # DQN agent implementation
├── environments/
│   ├── stick_hero_env.py     # Main game environment
│   ├── ai_env.py            # Simplified AI training environment
│   └── manual_game.py       # Manual gameplay interface
├── training/
│   └── trainer.py           # Training pipeline and utilities
├── ui/
│   └── terminal_ui.py       # Beautiful terminal interface
├── models/                  # Saved AI models
├── play_game.py            # Main game launcher
├── train_ai.py             # Training script
└── requirements.txt        # Dependencies
```

## Models

Pre-trained models are saved in the `models/` directory with performance metrics:
- `dqn_stick_hero_1000ep.pth` - Basic trained model (1000 episodes)
- `dqn_stick_hero_1500ep.pth` - Advanced model (1500 episodes, 85% success rate)
- `Pre-Trained.pth` - Hard mode specialist (5000 episodes)

## Dependencies

- **pygame** >= 2.5.2 - Game graphics and input handling
- **numpy** >= 1.24.3 - Numerical computations and state management
- **torch** >= 2.2.0 - Deep learning framework for DQN implementation

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Authors

- SMOTER Noa ([LinkedIn](https://www.linkedin.com/in/noa-smoter/) / [Portfolio](https://noasmoter.vercel.app/))