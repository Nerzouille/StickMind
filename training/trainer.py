"""
Functions for training and testing the Stick Hero AI
"""
import time
import numpy as np
from collections import deque
import os
import sys

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environments.ai_env import StickHeroAIEnv
from agents.dqn_agent import DQNAgent
from ui.terminal_ui import (Style, print_title, print_subtitle, print_status,
                           print_metric, loading_dots, progress_line)

def train_agent(episodes=1000):
    """Train the agent with accelerated learning"""
    print_title("🚀 Training Stick Hero AI")

    loading_dots("Initialization")

    env = StickHeroAIEnv()
    agent = DQNAgent(env.get_state_size(), env.get_action_size())

    # Clean configuration
    print_subtitle("AI Configuration")
    device_color = Style.SUCCESS if "cuda" in str(agent.device) else Style.WARNING
    print_status("🖥️", "Device", f"{agent.device}", device_color)
    print_status("🧠", "Architecture", f"{env.get_state_size()}→{env.get_action_size()}")
    print_status("📚", "Mémoire", f"{agent.memory.maxlen:,}")

    scores = []
    recent_scores = deque(maxlen=50)
    best_score = 0

    print(f"\n{Style.MUTED}  Episodes: {episodes} | Batch: 16 | Max steps: 50{Style.RESET}")
    print()  # Empty line for the beginning of the animation

    start_time = time.time()
    display_started = False

    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        steps = 0
        episode_loss = 0

        while not env.game_over and steps < 50:
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            steps += 1

            if len(agent.memory) > 16:
                loss = agent.replay(16)
                episode_loss += loss

        scores.append(env.score)
        recent_scores.append(env.score)

        if env.score > best_score:
            best_score = env.score

        # Real-time animated display
        if episode % 10 == 0 or episode == episodes - 1:
            if display_started:
                # Go up 6 lines and clear entire block
                print("\033[6A", end='')  # Go up
                for _ in range(6):
                    print("\033[2K\033[1B", end='')  # Clear line + go down
                print("\033[6A", end='')  # Go back up to start
            else:
                display_started = True

            # Progress bar
            progress_line(episode + 1, episodes, "Training")
            print()  # New line after the bar

            avg_score = np.mean(recent_scores) if recent_scores else 0
            elapsed = time.time() - start_time
            eps_per_sec = (episode + 1) / elapsed if elapsed > 0 else 0

            # Colors based on performance
            score_color = Style.SUCCESS if avg_score >= 5 else Style.WARNING if avg_score >= 2 else Style.WHITE

            # Compact display on multiple lines that replace each other
            print(f"  Episode: {Style.PRIMARY}{episode+1:4d}{Style.RESET}/{episodes}")
            print(f"  Avg score: {score_color}{avg_score:5.1f}{Style.RESET} | Record: {Style.SUCCESS if best_score >= 5 else Style.WHITE}{best_score:2d}{Style.RESET}")
            print(f"  Speed: {eps_per_sec:5.1f} eps/s | Epsilon: {Style.ACCENT}{agent.epsilon:5.3f}{Style.RESET}")
            print(f"  {Style.MUTED}Last scores: {list(recent_scores)[-5:] if recent_scores else []}{Style.RESET}")
            print()  # Empty line for the next animation

        # Less frequent save
        if (episode + 1) % 500 == 0:
            filename = f"stick_hero_simple2_{episode+1}.pt"
            agent.save(filename)
            # Temporary save display that doesn't break the animation
            print(f"\r{Style.SUCCESS}💾 Saved: {filename}{Style.RESET}")
            time.sleep(0.5)  # Short pause to see the message

        # Early stopping
        if np.mean(recent_scores) >= 20 and len(recent_scores) >= 50:
            print(f"\n{Style.SUCCESS}🎉 Objectif atteint! Score: {np.mean(recent_scores):.1f}{Style.RESET}")
            break
    
    # Final results
    print_title("🏆 Training finished")
    print_metric("Best score", best_score, color=Style.SUCCESS)
    print_metric("Final score", f"{np.mean(recent_scores):.1f}", color=Style.SUCCESS)
    print_metric("Total time", f"{(time.time() - start_time)/60:.1f} min")

    # Final save
    final_filename = f"stick_hero_simple2_final_{episodes}.pt"
    agent.save(final_filename)
    print_status("💾", "Final model", final_filename, Style.SUCCESS)

    return agent, scores

def test_agent(model_path, episodes=10):
    """Test the trained agent"""
    print_title("🧪 Test the AI agent")
    print_subtitle(f"Model: {model_path}")

    loading_dots("Loading the model")

    env = StickHeroAIEnv()
    agent = DQNAgent(env.get_state_size(), env.get_action_size())

    try:
        agent.load(model_path)
        agent.epsilon = 0
        print_status("✅", "Model loaded", color=Style.SUCCESS)
    except Exception as e:
        print_status("❌", f"Error: {e}", color=Style.ERROR)
        return

    scores = []

    for episode in range(episodes):
        state = env.reset()
        steps = 0
        total_reward = 0

        print(f"\n  Episode {episode+1}/{episodes}: Gap={env.gap_distance}, Width={env.next_platform_width}")

        while not env.game_over and steps < 50:
            action = agent.act(state)
            state, reward, done = env.step(action)
            total_reward += reward
            steps += 1

            if action == 1:  # Placement
                result_color = Style.SUCCESS if not env.game_over else Style.ERROR
                result_text = "✅ Success" if not env.game_over else "❌ Failure"
                print(f"    Stick: {env.stick_length} → {result_color}{result_text}{Style.RESET}")
                break

        scores.append(env.score)
        score_color = Style.SUCCESS if env.score >= 3 else Style.WARNING if env.score >= 1 else Style.WHITE
        print(f"    Score: {score_color}{env.score}{Style.RESET}, Reward: {total_reward:+.1f}")

    # Results
    print_title("📊 Results")
    success_rate = (np.array(scores) > 0).mean() * 100
    success_color = Style.SUCCESS if success_rate >= 70 else Style.WARNING if success_rate >= 40 else Style.ERROR

    print_metric("Average score", f"{np.mean(scores):.1f}")
    print_metric("Max score", max(scores))
    print_metric("Success rate", f"{success_rate:.0f}%", color=success_color)

def list_models():
    """List the available models with details"""
    models = []
    if os.path.exists('models'):
        for f in os.listdir('models'):
            if f.endswith('.pt'):
                model_path = os.path.join('models', f)
                size = os.path.getsize(model_path) / 1024
                mtime = os.path.getmtime(model_path)
                date = time.strftime('%d/%m %H:%M', time.localtime(mtime))
                models.append({
                    'name': f,
                    'details': f"{size:.0f}KB • {date}"
                })
    return models