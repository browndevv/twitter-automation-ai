# Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve common issues with the Twitter Automation AI system. Issues are organized by category with step-by-step solutions.

## Quick Diagnostics

### System Health Check

Run this command to quickly check system status:

```bash
python -c "
import asyncio
from src.core.config_loader import ConfigLoader
from src.core.llm_service import LLMService

async def health_check():
    try:
        config = ConfigLoader()
        print(f'✓ Configuration loaded: {bool(config.get_settings())}')
        
        llm = LLMService(config)
        print(f'✓ LLM services initialized')
        
        response = await llm.generate_text('Health check test')
        print(f'✓ LLM service working: {bool(response)}')
        
        print('\n✅ System appears healthy')
    except Exception as e:
        print(f'❌ System health check failed: {e}')

asyncio.run(health_check())
"
```

### Log Analysis

Check recent logs for errors:

```bash
# View recent logs
tail -50 logs/twitter_automation.log

# Look for errors
grep -i "error" logs/twitter_automation.log | tail -10

# Check LLM service status
grep "llm_service" logs/twitter_automation.log | tail -10
```

## API and Authentication Issues

### GitHub Copilot API Key Problems

#### Issue: "GitHub Copilot API key not configured"

**Symptoms**:
```
INFO - llm_service - GitHub Copilot API key not configured or is a placeholder
```

**Solutions**:

1. **Check API key format**:
   ```bash
   # Should start with 'ghu_'
   echo $GITHUB_COPILOT_API_KEY | head -c 4
   # Expected output: ghu_
   ```

2. **Verify key in configuration**:
   ```bash
   python -c "
   from src.core.config_loader import ConfigLoader
   config = ConfigLoader()
   key = config.get_api_key('copilot_api_key')
   print(f'Key found: {bool(key)}')
   print(f'Key starts with ghu_: {key and key.startswith(\"ghu_\")}')
   "
   ```

3. **Test API key directly**:
   ```bash
   curl -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY" \
        -H "Content-Type: application/json" \
        -H "Copilot-Integration-Id: vscode-chat" \
        -d '{"model":"gpt-4","messages":[{"role":"user","content":"test"}],"max_tokens":10}' \
        https://api.githubcopilot.com/chat/completions
   ```

#### Issue: "HTTP 401 Unauthorized"

**Symptoms**:
```
ERROR - llm_service - GitHub Copilot API request failed: 401 Unauthorized
```

**Solutions**:

1. **Regenerate API key**:
   - Go to GitHub Settings → Personal access tokens
   - Revoke current token
   - Generate new token with Copilot access

2. **Check token permissions**:
   - Ensure token has GitHub Copilot access
   - Verify account has Copilot subscription

3. **Update configuration**:
   ```bash
   # Update environment variable
   export GITHUB_COPILOT_API_KEY="new_key_here"
   
   # Or update .env file
   echo "GITHUB_COPILOT_API_KEY=new_key_here" > .env
   ```

#### Issue: "HTTP 429 Rate Limit Exceeded"

**Symptoms**:
```
ERROR - llm_service - GitHub Copilot API request failed: 429 Too Many Requests
```

**Solutions**:

1. **Adjust cycle frequency**:
   ```json
   {
     "agent_settings": {
       "cycle_interval_minutes": 60
     }
   }
   ```

2. **Implement request delays**:
   ```json
   {
     "llm_settings": {
       "copilot": {
         "default_params": {
           "request_delay": 2
         }
       }
     }
   }
   ```

### OpenAI API Issues

#### Issue: "OpenAI API key invalid"

**Solutions**:

1. **Verify key format**:
   ```bash
   # Should start with 'sk-'
   echo $OPENAI_API_KEY | head -c 3
   # Expected output: sk-
   ```

2. **Test API access**:
   ```bash
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}],"max_tokens":5}' \
        https://api.openai.com/v1/chat/completions
   ```

## Configuration Issues

### JSON Configuration Errors

#### Issue: "JSON decode error"

**Symptoms**:
```
ERROR - config_loader - Failed to parse settings.json: Expecting ',' delimiter
```

**Solutions**:

1. **Validate JSON syntax**:
   ```bash
   python -m json.tool config/settings.json
   ```

2. **Common JSON fixes**:
   - Remove trailing commas
   - Ensure proper quote usage
   - Check bracket matching

3. **Use JSON validator**:
   ```bash
   python -c "
   import json
   try:
       with open('config/settings.json') as f:
           json.load(f)
       print('✓ JSON is valid')
   except json.JSONDecodeError as e:
       print(f'❌ JSON error: {e}')
   "
   ```

#### Issue: "Missing required configuration"

**Symptoms**:
```
ERROR - config_loader - Required setting 'api_keys' not found
```

**Solutions**:

1. **Check configuration structure**:
   ```json
   {
     "api_keys": {
       "copilot_api_key": "your_key"
     },
     "llm_settings": {
       "service_preference_order": ["copilot"]
     }
   }
   ```

2. **Validate against template**:
   ```bash
   diff config/settings.json.template config/settings.json
   ```

### Account Configuration Issues

#### Issue: "Account not found"

**Symptoms**:
```
ERROR - orchestrator - Account 'username' not found in configuration
```

**Solutions**:

1. **Check accounts.json**:
   ```bash
   python -c "
   import json
   with open('config/accounts.json') as f:
       accounts = json.load(f)
   print('Configured accounts:', list(accounts.get('accounts', {}).keys()))
   "
   ```

2. **Add missing account**:
   ```json
   {
     "accounts": {
       "your_username": {
         "username": "your_username",
         "display_name": "Your Name",
         "target_keywords": ["keyword1", "keyword2"],
         "personality_prompt": "Your brand voice"
       }
     }
   }
   ```

## Goal and Task Issues

### Goal Parsing Problems

#### Issue: "Failed to parse goal"

**Symptoms**:
```
ERROR - orchestrator - Failed to parse goal: validation errors for AgentGoal
```

**Solutions**:

1. **Use specific numeric targets**:
   ```
   Good: "Gain 500 followers in 30 days"
   Bad: "Get more followers soon"
   ```

2. **Include timeframes**:
   ```
   Good: "Increase engagement to 5% by end of month"
   Bad: "Improve engagement sometime"
   ```

3. **Check validation errors**:
   ```bash
   grep "validation errors" logs/twitter_automation.log -A 5
   ```

#### Issue: "Invalid agent role in task"

**Symptoms**:
```
ERROR - core_agent - 'content_optimizer' is not a valid AgentRole
```

**Solutions**:

1. **Check valid roles**:
   ```python
   from src.agents.core_agent import AgentRole
   print("Valid roles:", [role.value for role in AgentRole])
   ```

2. **Update LLM prompts**:
   The system should only use these roles:
   - `strategist`
   - `content_creator`
   - `content_curator`
   - `engagement_manager`
   - `performance_analyst`

### Task Execution Issues

#### Issue: "Task timeout"

**Symptoms**:
```
ERROR - orchestrator - Task execution timeout after 300 seconds
```

**Solutions**:

1. **Increase timeout**:
   ```json
   {
     "agent_settings": {
       "task_timeout_seconds": 600
     }
   }
   ```

2. **Check task complexity**:
   - Break down complex tasks
   - Simplify task parameters

#### Issue: "Browser automation failed"

**Symptoms**:
```
ERROR - browser_manager - WebDriver initialization failed
```

**Solutions**:

1. **Update WebDriver**:
   ```bash
   python -c "
   from webdriver_manager.chrome import ChromeDriverManager
   ChromeDriverManager().install()
   "
   ```

2. **Check browser installation**:
   ```bash
   # Check Chrome
   google-chrome --version
   
   # Check Firefox
   firefox --version
   ```

3. **Use headless mode**:
   ```json
   {
     "browser_settings": {
       "headless": true
     }
   }
   ```

## Memory and Storage Issues

### JSON Serialization Errors

#### Issue: "Object of type datetime is not JSON serializable"

**Symptoms**:
```
ERROR - memory_manager - Failed to save context: Object of type datetime is not JSON serializable
```

**Solutions**:

1. **Check datetime handling**:
   The system should automatically convert datetime objects to ISO format

2. **Manual fix** (if needed):
   ```python
   # In memory_manager.py, ensure datetime conversion
   "last_updated": context.memory.last_updated.isoformat()
   ```

### Storage Permission Issues

#### Issue: "Permission denied writing to agent_memory"

**Solutions**:

1. **Fix permissions**:
   ```bash
   chmod -R 755 agent_memory/
   chown -R $USER:$USER agent_memory/
   ```

2. **Check disk space**:
   ```bash
   df -h .
   ```

## Network and Connectivity Issues

### API Connectivity Problems

#### Issue: "Connection timeout"

**Symptoms**:
```
ERROR - llm_service - Error using copilot LLM: ConnectTimeout
```

**Solutions**:

1. **Check internet connectivity**:
   ```bash
   ping api.githubcopilot.com
   curl -I https://api.githubcopilot.com
   ```

2. **Increase timeout**:
   ```json
   {
     "llm_settings": {
       "copilot": {
         "timeout": 120
       }
     }
   }
   ```

3. **Check firewall/proxy**:
   - Ensure HTTPS traffic allowed
   - Configure proxy if needed

### DNS Resolution Issues

#### Issue: "Name resolution failed"

**Solutions**:

1. **Check DNS**:
   ```bash
   nslookup api.githubcopilot.com
   nslookup api.openai.com
   ```

2. **Use alternative DNS**:
   ```bash
   # Use Google DNS
   echo "nameserver 8.8.8.8" >> /etc/resolv.conf
   ```

## Performance Issues

### Slow Response Times

#### Issue: "LLM responses taking too long"

**Solutions**:

1. **Check response times**:
   ```bash
   grep "Successfully generated text" logs/twitter_automation.log | tail -10
   ```

2. **Optimize parameters**:
   ```json
   {
     "llm_settings": {
       "copilot": {
         "default_params": {
           "max_tokens": 250,
           "temperature": 0.7
         }
       }
     }
   }
   ```

3. **Use faster models**:
   ```json
   {
     "llm_settings": {
       "service_preference_order": ["copilot", "openai"]
     }
   }
   ```

### Memory Usage Issues

#### Issue: "High memory consumption"

**Solutions**:

1. **Monitor memory usage**:
   ```bash
   ps aux | grep python
   ```

2. **Reduce concurrent tasks**:
   ```json
   {
     "agent_settings": {
       "max_concurrent_accounts": 1,
       "max_concurrent_tasks": 2
     }
   }
   ```

3. **Clear browser cache**:
   ```bash
   rm -rf .wdm_cache/
   ```

## Platform-Specific Issues

### Windows Issues

#### Issue: "PowerShell execution policy"

**Solutions**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: "Long path names"

**Solutions**:
```powershell
# Enable long paths
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### macOS Issues

#### Issue: "Certificate verification failed"

**Solutions**:
```bash
# Update certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

#### Issue: "Xcode command line tools missing"

**Solutions**:
```bash
xcode-select --install
```

### Linux Issues

#### Issue: "Display server not found"

**Solutions**:
```bash
# For headless operation
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

#### Issue: "Chrome dependencies missing"

**Solutions**:
```bash
sudo apt-get install -y \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2
```

## Debugging Techniques

### Enable Debug Logging

1. **Increase log level**:
   ```json
   {
     "logging": {
       "level": "DEBUG"
     }
   }
   ```

2. **Component-specific debugging**:
   ```json
   {
     "logging": {
       "debug_modules": ["llm_service", "orchestrator", "core_agent"]
     }
   }
   ```

### Trace LLM Interactions

```bash
# Monitor LLM requests
grep "Attempting to generate text" logs/twitter_automation.log -A 3 -B 1

# Check response times
grep "Successfully generated text" logs/twitter_automation.log | \
  awk '{print $1, $2, $NF}' | tail -10
```

### Test Individual Components

```python
# Test configuration loading
python -c "
from src.core.config_loader import ConfigLoader
config = ConfigLoader()
print('Settings:', bool(config.get_settings()))
print('Accounts:', len(config.get_setting('accounts', {}).get('accounts', {})))
"

# Test LLM service
python -c "
import asyncio
from src.core.config_loader import ConfigLoader
from src.core.llm_service import LLMService

async def test_llm():
    config = ConfigLoader()
    llm = LLMService(config)
    response = await llm.generate_text('Test message', max_tokens=50)
    print(f'LLM Response: {response[:100] if response else None}')

asyncio.run(test_llm())
"
```

## Getting Help

### Information to Include

When seeking help, provide:

1. **System information**:
   ```bash
   python --version
   pip list | grep -E "(httpx|openai|selenium)"
   ```

2. **Configuration (sanitized)**:
   ```bash
   python -c "
   import json
   from src.core.config_loader import ConfigLoader
   config = ConfigLoader()
   settings = config.get_settings()
   # Remove sensitive info
   if 'api_keys' in settings:
       settings['api_keys'] = {k: 'REDACTED' for k in settings['api_keys']}
   print(json.dumps(settings, indent=2))
   "
   ```

3. **Recent error logs**:
   ```bash
   grep -i "error" logs/twitter_automation.log | tail -20
   ```

4. **Steps to reproduce**: Clear description of what you were doing when the issue occurred

### Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check all documentation files
- **Examples**: Review working configuration examples

---

*This troubleshooting guide covers the most common issues. For persistent problems, enable debug logging and examine the detailed error messages for specific guidance.*
