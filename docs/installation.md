# Installation Guide

## System Requirements

### Python Environment
- **Python Version**: 3.8 or higher (3.10+ recommended)
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space for dependencies and data

### API Requirements
- **GitHub Copilot API Key** (primary requirement)
- **OpenAI API Key** (optional, for fallback)
- **Azure OpenAI Access** (optional, for enterprise)

## Installation Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/browndevv/twitter-automation-ai.git
cd twitter-automation-ai

# Or download and extract ZIP file
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import asyncio, httpx, openai; print('Dependencies installed successfully')"
```

### Step 4: Create Configuration Files

```bash
# Create configuration directory (if not exists)
mkdir -p config

# Copy template files
cp config/settings.json.template config/settings.json
cp config/accounts.json.template config/accounts.json
```

### Step 5: Configure API Keys

#### Option A: Environment Variables (Recommended)

Create `.env` file in project root:

```bash
# Create .env file
touch .env

# Add your API keys
echo "GITHUB_COPILOT_API_KEY=ghu_your_actual_api_key_here" >> .env
```

#### Option B: Direct Configuration

Edit `config/settings.json`:

```json
{
  "api_keys": {
    "copilot_api_key": "ghu_your_actual_api_key_here"
  }
}
```

### Step 6: Configure Account Settings

Edit `config/accounts.json`:

```json
{
  "accounts": {
    "your_username": {
      "username": "your_username",
      "display_name": "Your Display Name",
      "target_keywords": ["keyword1", "keyword2", "keyword3"],
      "personality_prompt": "Your brand voice description"
    }
  }
}
```

### Step 7: Test Installation

```bash
# Test basic functionality
python main.py

# You should see the interactive menu
```

## Detailed Configuration

### Required Configuration

#### GitHub Copilot API Key

1. **Obtain Key**:
   - Go to [GitHub Settings](https://github.com/settings/tokens)
   - Navigate to Developer settings → Personal access tokens
   - Generate new token with Copilot access
   - Copy the token (starts with `ghu_`)

2. **Configure**:
   ```bash
   export GITHUB_COPILOT_API_KEY="ghu_your_actual_key"
   ```

#### Account Configuration

Minimal account setup in `config/accounts.json`:

```json
{
  "accounts": {
    "your_handle": {
      "username": "your_handle",
      "display_name": "Your Name",
      "target_keywords": ["ai", "automation", "tech"],
      "personality_prompt": "Professional tech enthusiast sharing insights about AI and automation"
    }
  }
}
```

### Optional Configuration

#### Additional LLM Services

**OpenAI Configuration**:

```json
{
  "api_keys": {
    "openai_api_key": "sk-your_openai_key"
  },
  "llm_settings": {
    "service_preference_order": ["copilot", "openai"],
    "openai": {
      "model": "gpt-4",
      "default_params": {
        "temperature": 0.7,
        "max_tokens": 300
      }
    }
  }
}
```

**Azure OpenAI Configuration**:

```json
{
  "api_keys": {
    "azure_openai_api_key": "your_azure_key",
    "azure_openai_endpoint": "https://your-resource.openai.azure.com/",
    "azure_openai_deployment": "your-deployment-name"
  },
  "llm_settings": {
    "azure": {
      "deployment_name": "gpt-4",
      "api_version": "2024-05-01-preview"
    }
  }
}
```

## Advanced Installation Options

### Docker Installation

#### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create configuration directory
RUN mkdir -p config logs

# Set environment variables
ENV PYTHONPATH=/app

# Expose port (if needed)
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

#### Build and Run

```bash
# Build Docker image
docker build -t twitter-automation-ai .

# Run container
docker run -d \
  -e GITHUB_COPILOT_API_KEY=your_key \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  twitter-automation-ai
```

### Production Installation

#### System Service Setup (Linux)

Create systemd service file `/etc/systemd/system/twitter-ai.service`:

```ini
[Unit]
Description=Twitter Automation AI
After=network.target

[Service]
Type=simple
User=twitter-ai
WorkingDirectory=/opt/twitter-automation-ai
Environment=PYTHONPATH=/opt/twitter-automation-ai
Environment=GITHUB_COPILOT_API_KEY=your_key
ExecStart=/opt/twitter-automation-ai/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl enable twitter-ai
sudo systemctl start twitter-ai
sudo systemctl status twitter-ai
```

#### Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'twitter-automation-ai',
    script: 'python',
    args: 'main.py',
    cwd: '/path/to/twitter-automation-ai',
    env: {
      GITHUB_COPILOT_API_KEY: 'your_key'
    },
    restart_delay: 10000
  }]
};
EOF

# Start application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Dependencies

### Core Dependencies

```txt
# requirements.txt core dependencies
asyncio>=3.4.3
httpx>=0.24.0
openai>=1.0.0
selenium>=4.0.0
webdriver-manager>=3.8.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### Optional Dependencies

```txt
# Optional LLM services
langchain-google-genai>=1.0.0  # For Gemini support
azure-openai>=1.0.0           # For Azure OpenAI

# Development dependencies
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
```

### Browser Dependencies

The system automatically manages WebDriver installation, but you can install browsers manually:

**Chrome/Chromium**:
```bash
# Ubuntu/Debian
sudo apt-get install google-chrome-stable

# macOS
brew install --cask google-chrome

# Windows
# Download from Google Chrome website
```

**Firefox**:
```bash
# Ubuntu/Debian
sudo apt-get install firefox

# macOS
brew install --cask firefox

# Windows
# Download from Mozilla website
```

## Verification

### Test Installation

```bash
# Basic import test
python -c "
from src.core.config_loader import ConfigLoader
from src.core.llm_service import LLMService
from src.agents.orchestrator import AgentOrchestrator
print('All imports successful')
"

# Configuration test
python -c "
from src.core.config_loader import ConfigLoader
config = ConfigLoader()
print(f'Configuration loaded: {bool(config.get_settings())}')
"

# LLM service test
python -c "
import asyncio
from src.core.config_loader import ConfigLoader
from src.core.llm_service import LLMService

async def test():
    config = ConfigLoader()
    llm = LLMService(config)
    response = await llm.generate_text('Hello, test message')
    print(f'LLM test: {bool(response)}')

asyncio.run(test())
"
```

### Performance Test

```bash
# Run performance benchmark
python -c "
import time
import asyncio
from src.core.config_loader import ConfigLoader
from src.core.llm_service import LLMService

async def benchmark():
    config = ConfigLoader()
    llm = LLMService(config)
    
    start_time = time.time()
    response = await llm.generate_text('Write a short tweet about AI')
    end_time = time.time()
    
    print(f'Response time: {end_time - start_time:.2f} seconds')
    print(f'Response length: {len(response) if response else 0} characters')

asyncio.run(benchmark())
"
```

## Troubleshooting Installation

### Common Issues

#### Python Version Issues

```bash
# Check Python version
python --version

# Use specific Python version
python3.10 -m venv venv
```

#### Dependency Conflicts

```bash
# Clean installation
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# Or use fresh virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Permission Issues

```bash
# Linux/macOS permission fix
chmod +x main.py
sudo chown -R $USER:$USER .

# Windows permission fix (run as administrator)
```

#### WebDriver Issues

```bash
# Clear WebDriver cache
rm -rf ~/.wdm
rm -rf .wdm_cache

# Manual WebDriver installation
python -c "
from webdriver_manager.chrome import ChromeDriverManager
ChromeDriverManager().install()
"
```

### Environment-Specific Issues

#### Windows

```powershell
# Enable execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Visual C++ Build Tools if needed
# Download from Microsoft website
```

#### macOS

```bash
# Install Xcode command line tools
xcode-select --install

# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Linux

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv

# Install Chrome dependencies
sudo apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb
```

## Directory Structure After Installation

```
twitter-automation-ai/
├── config/
│   ├── settings.json
│   ├── accounts.json
│   └── *.json (other config files)
├── src/
│   ├── agents/
│   ├── core/
│   └── utils/
├── docs/
├── logs/
├── agent_memory/
├── venv/
├── main.py
├── requirements.txt
├── .env
└── README.md
```

## Next Steps

After successful installation:

1. **Configure your first account** in `config/accounts.json`
2. **Set your first goal** using the interactive menu
3. **Run a single cycle** to test functionality
4. **Monitor logs** for any issues
5. **Adjust configuration** based on performance

## Security Considerations

### API Key Security

- Never commit API keys to version control
- Use environment variables for production
- Rotate keys regularly
- Monitor API usage and costs

### File Permissions

```bash
# Secure configuration files
chmod 600 config/settings.json
chmod 600 .env

# Secure log directory
chmod 755 logs/
```

### Network Security

- Use HTTPS for all API calls (default)
- Consider VPN for sensitive operations
- Monitor network traffic for anomalies

---

*Installation complete! Your Twitter Automation AI system is ready to use. Proceed to the User Guide for operational instructions.*
