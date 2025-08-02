# Agentic Twitter Automation

An AI-powered, autonomous Twitter automation system that uses LLM agents to make intelligent decisions about content creation, curation, engagement, and performance optimization.

## Features

🤖 **Autonomous Agent Architecture**

- AI agents that make intelligent decisions about Twitter activities
- Specialized agents for content creation, curation, engagement, and analytics
- Self-learning system that adapts based on performance

🧠 **Natural Language Goal Setting**

- Set goals in plain English: "Increase engagement by 20%" or "Create viral content about AI"
- LLM-powered goal interpretation and strategic planning
- Dynamic task generation based on your objectives

💾 **Memory & Learning System**

- Persistent memory that tracks performance and learns from actions
- Context-aware decision making based on past results
- Adaptive strategies that improve over time

🔄 **Real-time Adaptation**

- Continuous monitoring and strategy adjustment
- Performance-based optimization
- Dynamic response to Twitter trends and engagement patterns

## Quick Start

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   Add your LLM API key to `.env`:

   ```
   GITHUB_COPILOT_API_KEY=your_copilot_key
   # OR
   OPENAI_API_KEY=your_openai_key
   # OR  
   GEMINI_API_KEY=your_gemini_key
   ```

3. **Configure Twitter Account**
   Edit `config/accounts.json` with your Twitter account details and cookies.

4. **Run Interactive Mode**

   ```bash
   python main.py --mode interactive
   ```

5. **Add Goals**
   In interactive mode, select "Add new goal" and describe what you want to achieve in natural language.

## Usage Modes

### Interactive Mode

```bash
python main.py --mode interactive
```

Menu-driven interface for managing goals, viewing status, and running cycles.

### Continuous Mode  

```bash
python main.py --mode continuous
```

Runs autonomously, executing agent decisions in real-time.

### Single Cycle

```bash
python main.py --mode single-cycle
```

Runs one execution cycle across all accounts.

### Command Line Goal Setting

```bash
python main.py --goal "Increase followers by 50% this month" --goal-account browndevv
```

## Architecture

- `main.py` - Main entry point and CLI interface
- `src/agents/` - Core agentic system
  - `orchestrator.py` - Coordinates multiple agents and accounts
  - `core_agent.py` - Central decision-making AI agent
  - `specialized_agents.py` - Task-specific agents (content, engagement, etc.)
  - `memory_manager.py` - Persistent memory and learning system
- `src/core/` - Core services (LLM, configuration)
- `src/utils/` - Utilities (logging, file handling)

## Configuration

### Accounts (`config/accounts.json`)

Configure Twitter accounts with authentication cookies.

### Settings (`config/settings.json`)

Configure LLM preferences, automation settings, and API keys.

### Environment (`.env`)

Store sensitive API keys securely.

## Requirements

- Python 3.8+
- LLM API access (OpenAI, Gemini, or GitHub Copilot)
- Twitter account with valid authentication cookies

## License

MIT License - see LICENSE file for details.
