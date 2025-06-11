"""
Agent DQN for Stick Hero AI
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import os

class SimpleNet(nn.Module):
    """Simple neural network for fast learning"""
    def __init__(self, input_size, output_size, hidden_size=64):
        super(SimpleNet, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.network(x)

class DQNAgent:
    """Simplified DQN agent for fast learning"""

    def __init__(self, state_size, action_size, learning_rate=0.003):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)

        # Parameters for maximum speed learning
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99  # Fast decay
        self.learning_rate = learning_rate
        self.gamma = 0.9  # Focus on immediate rewards

        # Simple network
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = SimpleNet(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

    def remember(self, state, action, reward, next_state, done):
        """Store the experience"""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """Choose an action (epsilon-greedy)"""
        if random.random() <= self.epsilon:
            return random.randrange(self.action_size)

        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.q_network(state_tensor)
        return np.argmax(q_values.cpu().data.numpy())

    def replay(self, batch_size=32):
        """Train the network"""
        if len(self.memory) < batch_size:
            return 0

        batch = random.sample(self.memory, batch_size)

        states_np = np.array([e[0] for e in batch])
        next_states_np = np.array([e[3] for e in batch])

        states = torch.FloatTensor(states_np).to(self.device)
        actions = torch.LongTensor([e[1] for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e[2] for e in batch]).to(self.device)
        next_states = torch.FloatTensor(next_states_np).to(self.device)
        dones = torch.BoolTensor([e[4] for e in batch]).to(self.device)

        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.q_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * ~dones)

        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return loss.item()

    def save(self, filename):
        """Save the model"""
        os.makedirs("models", exist_ok=True)
        filepath = os.path.join("models", filename)
        torch.save({
            'model_state_dict': self.q_network.state_dict(),
            'epsilon': self.epsilon
        }, filepath)

    def load(self, filename):
        """Load the model"""
        if not filename.startswith("models/"):
            filepath = os.path.join("models", filename)
        else:
            filepath = filename
        checkpoint = torch.load(filepath)
        self.q_network.load_state_dict(checkpoint['model_state_dict'])
        self.epsilon = checkpoint.get('epsilon', 0.01)