# Configuration Guide

## Overview

This guide covers all configuration aspects of the Twitter Automation AI system, including API keys, system settings, and account-specific configurations.

## Configuration Files

### 1. Main Settings (`config/settings.json`)

The primary configuration file that controls system behavior:

```json
{
  "api_keys": {
    "copilot_api_key": "YOUR_GITHUB_COPILOT_API_KEY",
    "openai_api_key": "YOUR_OPENAI_API_KEY",
    "azure_openai_api_key": "YOUR_AZURE_OPENAI_API_KEY",
    "azure_openai_endpoint": "YOUR_AZURE_OPENAI_ENDPOINT",
    "azure_openai_deployment": "YOUR_AZURE_DEPLOYMENT_NAME"
  },
  "llm_settings": {
    "service_preference_order": ["copilot", "azure", "openai", "gemini"],
    "default_max_tokens": 250,
    "copilot": {
      "model": "gpt-4",
      "default_params": {
        "temperature": 0.7,
        "max_tokens": 500
      }
    },
    "openai": {
      "model": "gpt-4",
      "default_params": {
        "temperature": 0.7,
        "max_tokens": 300
      }
    },
    "azure": {
      "deployment_name": "your-deployment-name",
      "api_version": "2024-05-01-preview",
      "default_params": {
        "temperature": 0.75,
        "max_tokens": 300
      }
    }
  },
  "browser_settings": {
    "default_browser": "chrome",
    "headless": true,
    "window_size": [1920, 1080],
    "user_agent_rotation": true,
    "wait_times": {
      "page_load": 10,
      "element_wait": 5,
      "action_delay": [1, 3]
    }
  },
  "agent_settings": {
    "cycle_interval_minutes": 1,
    "max_concurrent_accounts": 3,
    "task_timeout_seconds": 300,
    "max_retries": 3
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": true,
    "log_file": "logs/twitter_automation.log"
  }
}
```

### 2. Account Configuration (`config/accounts.json`)

Account-specific settings and credentials:

```json
{
  "accounts": {
    "browndevv": {
      "username": "browndevv",
      "display_name": "Brown Developer",
      "bio": "AI Engineer & Developer",
      "target_keywords": ["AI", "automation", "programming", "technology"],
      "competitor_profiles": ["@elonmusk", "@sama", "@karpathy"],
      "personality_prompt": "Professional yet approachable tech expert who shares insights about AI and programming.",
      "content_strategy": {
        "post_frequency": "daily",
        "engagement_style": "thoughtful",
        "content_mix": {
          "original": 0.6,
          "curated": 0.3,
          "engagement": 0.1
        }
      },
      "goals": {
        "follower_target": 10000,
        "engagement_rate_target": 0.05,
        "posts_per_week": 7
      }
    }
  }
}
```

### 3. Environment Variables (`.env`)

Sensitive configuration data:

```bash
# GitHub Copilot API Key
GITHUB_COPILOT_API_KEY=ghu_your_actual_api_key_here

# OpenAI API Key
OPENAI_API_KEY=sk-your_openai_key_here

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Twitter API Credentials (for future integration)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Database Configuration (if using external DB)
DATABASE_URL=postgresql://user:password@localhost:5432/twitter_ai

# Security Settings
SECRET_KEY=your_secret_key_for_encryption
```

## API Key Setup

### 1. GitHub Copilot API Key

**Obtaining the Key:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with Copilot access
3. Copy the token (starts with `ghu_`)

**Configuration:**
```json
{
  "api_keys": {
    "copilot_api_key": "ghu_your_actual_key_here"
  }
}
```

### 2. OpenAI API Key

**Obtaining the Key:**
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key (starts with `sk-`)

**Configuration:**
```json
{
  "api_keys": {
    "openai_api_key": "sk-your_key_here"
  },
  "llm_settings": {
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

### 3. Azure OpenAI Setup

**Prerequisites:**
1. Azure subscription with OpenAI resource
2. Deployed model (e.g., GPT-4)
3. Endpoint URL and deployment name

**Configuration:**
```json
{
  "api_keys": {
    "azure_openai_api_key": "your_azure_key",
    "azure_openai_endpoint": "https://your-resource.openai.azure.com/",
    "azure_openai_deployment": "your-deployment-name"
  },
  "llm_settings": {
    "azure": {
      "deployment_name": "your-deployment-name",
      "api_version": "2024-05-01-preview"
    }
  }
}
```

## Advanced Configuration

### 1. LLM Service Priority

Configure which AI service to use first:

```json
{
  "llm_settings": {
    "service_preference_order": ["copilot", "openai", "azure", "gemini"]
  }
}
```

**Options:**
- `"copilot"`: GitHub Copilot (recommended)
- `"openai"`: OpenAI GPT models
- `"azure"`: Azure OpenAI
- `"gemini"`: Google Gemini

### 2. Agent Behavior Configuration

```json
{
  "agent_settings": {
    "cycle_interval_minutes": 30,
    "max_concurrent_accounts": 3,
    "task_timeout_seconds": 300,
    "max_retries": 3,
    "decision_threshold": 0.7,
    "planning_interval_hours": 1
  }
}
```

**Parameters:**
- `cycle_interval_minutes`: How often agents run (1-60 minutes)
- `max_concurrent_accounts`: Maximum accounts processed simultaneously
- `task_timeout_seconds`: Maximum time for task execution
- `max_retries`: Retry attempts for failed tasks
- `decision_threshold`: Confidence threshold for actions (0.0-1.0)

### 3. Browser Automation Settings

```json
{
  "browser_settings": {
    "default_browser": "chrome",
    "headless": true,
    "window_size": [1920, 1080],
    "user_agent_rotation": true,
    "proxy_settings": {
      "enabled": false,
      "proxy_list": []
    },
    "wait_times": {
      "page_load": 10,
      "element_wait": 5,
      "action_delay": [1, 3]
    },
    "anti_detection": {
      "random_delays": true,
      "human_like_scrolling": true,
      "viewport_randomization": true
    }
  }
}
```

### 4. Memory Management Configuration

```json
{
  "memory_settings": {
    "max_context_size": 1000,
    "cleanup_interval_days": 7,
    "performance_history_limit": 100,
    "goal_history_limit": 50,
    "auto_backup": true,
    "backup_interval_hours": 24
  }
}
```

### 5. Logging Configuration

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": true,
    "log_file": "logs/twitter_automation.log",
    "max_log_size_mb": 100,
    "backup_count": 5,
    "console_logging": true,
    "debug_modules": ["llm_service", "orchestrator"]
  }
}
```

**Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General information (recommended)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

## Account-Specific Configuration

### 1. Content Strategy

```json
{
  "content_strategy": {
    "post_frequency": "daily",
    "optimal_times": ["09:00", "15:00", "20:00"],
    "content_mix": {
      "original": 0.6,
      "curated": 0.3,
      "engagement": 0.1
    },
    "hashtag_strategy": {
      "max_hashtags": 3,
      "trending_weight": 0.3,
      "niche_weight": 0.7
    }
  }
}
```

### 2. Engagement Settings

```json
{
  "engagement_settings": {
    "auto_reply": {
      "enabled": true,
      "reply_rate": 0.3,
      "exclude_keywords": ["spam", "bot"]
    },
    "follow_back": {
      "enabled": true,
      "follow_rate": 0.1,
      "min_followers": 10
    },
    "like_strategy": {
      "enabled": true,
      "like_rate": 0.5,
      "target_accounts": true
    }
  }
}
```

### 3. Performance Targets

```json
{
  "performance_targets": {
    "followers": {
      "target": 10000,
      "monthly_growth": 500,
      "quality_threshold": 0.8
    },
    "engagement": {
      "target_rate": 0.05,
      "min_interactions": 100,
      "response_time_hours": 2
    },
    "content": {
      "posts_per_week": 7,
      "threads_per_month": 4,
      "viral_threshold": 1000
    }
  }
}
```

## Security Best Practices

### 1. API Key Security

```bash
# Use environment variables
export GITHUB_COPILOT_API_KEY="your_key_here"

# Or use .env file (never commit to version control)
echo "GITHUB_COPILOT_API_KEY=your_key_here" >> .env
```

### 2. Configuration Validation

The system automatically validates:

- API key format and accessibility
- Required configuration fields
- Value ranges and types
- Service availability

### 3. Backup Configuration

```json
{
  "backup_settings": {
    "auto_backup": true,
    "backup_location": "backups/",
    "encryption": true,
    "retention_days": 30
  }
}
```

## Troubleshooting Configuration

### Common Issues

1. **API Key Invalid**
   - Check key format (GitHub Copilot: `ghu_`, OpenAI: `sk-`)
   - Verify key has correct permissions
   - Ensure no extra spaces or characters

2. **Service Not Available**
   - Check network connectivity
   - Verify service endpoints
   - Review rate limiting

3. **Configuration Errors**
   - Validate JSON syntax
   - Check required fields
   - Review data types

### Validation Commands

```bash
# Test configuration
python -c "from src.core.config_loader import ConfigLoader; print(ConfigLoader().validate_config())"

# Test LLM services
python -c "from src.core.llm_service import LLMService; from src.core.config_loader import ConfigLoader; import asyncio; asyncio.run(LLMService(ConfigLoader()).generate_text('test'))"
```

## Configuration Templates

### Minimal Configuration

```json
{
  "api_keys": {
    "copilot_api_key": "YOUR_GITHUB_COPILOT_KEY"
  },
  "llm_settings": {
    "service_preference_order": ["copilot"]
  }
}
```

### Production Configuration

```json
{
  "api_keys": {
    "copilot_api_key": "YOUR_GITHUB_COPILOT_KEY",
    "openai_api_key": "YOUR_OPENAI_KEY"
  },
  "llm_settings": {
    "service_preference_order": ["copilot", "openai"],
    "default_max_tokens": 300
  },
  "agent_settings": {
    "cycle_interval_minutes": 30,
    "max_concurrent_accounts": 5
  },
  "browser_settings": {
    "headless": true,
    "anti_detection": {
      "random_delays": true,
      "human_like_scrolling": true
    }
  },
  "logging": {
    "level": "INFO",
    "file_logging": true
  }
}
```

---

*Remember to never commit API keys or sensitive configuration to version control. Use environment variables or encrypted configuration files for production deployments.*
