# API Reference

## Overview

This document provides detailed API documentation for all modules, classes, and methods in the Twitter Automation AI system.

## Core Modules

### 1. LLM Service (`src/core/llm_service.py`)

**Purpose**: Centralized AI service management with intelligent fallback capabilities.

#### Class: `LLMService`

```python
class LLMService:
    def __init__(self, config_loader: ConfigLoader)
```

**Constructor Parameters**:
- `config_loader`: ConfigLoader instance for accessing configuration

**Attributes**:
- `service_preference_order`: List of LLM services in priority order
- `gemini_client`: Google Gemini client instance
- `openai_client`: OpenAI API client instance
- `azure_openai_client`: Azure OpenAI client instance
- `copilot_client`: GitHub Copilot HTTP client instance

#### Methods

##### `generate_text()`

```python
async def generate_text(
    self,
    prompt: str,
    service_preference: Optional[str] = None,
    **call_params: Any
) -> Optional[str]
```

**Purpose**: Generate text using configured LLM services with automatic fallback.

**Parameters**:
- `prompt`: Text prompt for the LLM
- `service_preference`: Preferred service name ('copilot', 'openai', 'azure', 'gemini')
- `**call_params`: Additional parameters (model, max_tokens, temperature, etc.)

**Returns**: Generated text string or None if all services fail

**Example**:
```python
llm_service = LLMService(config_loader)
response = await llm_service.generate_text(
    "Write a tweet about AI",
    service_preference="copilot",
    max_tokens=280,
    temperature=0.7
)
```

##### `_initialize_clients()`

```python
def _initialize_clients(self) -> None
```

**Purpose**: Initialize all available LLM service clients based on configuration.

**Internal Method**: Called automatically during initialization.

##### `_is_api_key_valid()`

```python
def _is_api_key_valid(self, key_name: str, key_value: Optional[str]) -> bool
```

**Purpose**: Validate API key format and detect placeholders.

**Parameters**:
- `key_name`: Name of the API key
- `key_value`: Value to validate

**Returns**: True if key is valid, False otherwise

### 2. Config Loader (`src/core/config_loader.py`)

**Purpose**: Configuration management and environment variable handling.

#### Class: `ConfigLoader`

```python
class ConfigLoader:
    def __init__(self, config_dir: Optional[str] = None)
```

**Constructor Parameters**:
- `config_dir`: Optional custom configuration directory path

**Attributes**:
- `config_dir`: Path to configuration directory
- `settings_file`: Path to settings.json file
- `accounts_file`: Path to accounts.json file

#### Methods

##### `get_setting()`

```python
def get_setting(self, key: str, default: Any = None) -> Any
```

**Purpose**: Retrieve configuration setting with default fallback.

**Parameters**:
- `key`: Setting key (supports dot notation for nested keys)
- `default`: Default value if key not found

**Returns**: Configuration value or default

**Example**:
```python
config = ConfigLoader()
llm_settings = config.get_setting('llm_settings', {})
api_key = config.get_setting('api_keys.copilot_api_key')
```

##### `get_api_key()`

```python
def get_api_key(self, key_name: str) -> Optional[str]
```

**Purpose**: Retrieve API key from environment variables or configuration.

**Parameters**:
- `key_name`: Name of the API key

**Returns**: API key string or None if not found

**Example**:
```python
copilot_key = config.get_api_key('copilot_api_key')
```

##### `get_account_config()`

```python
def get_account_config(self, account_id: str) -> Optional[AccountConfig]
```

**Purpose**: Retrieve configuration for specific account.

**Parameters**:
- `account_id`: Account identifier

**Returns**: AccountConfig object or None if not found

### 3. Browser Manager (`src/core/browser_manager.py`)

**Purpose**: Web automation and browser control for Twitter interactions.

#### Class: `BrowserManager`

```python
class BrowserManager:
    def __init__(self, account_config: Optional[Dict] = None, config_loader: Optional[ConfigLoader] = None)
```

**Constructor Parameters**:
- `account_config`: Account-specific configuration
- `config_loader`: ConfigLoader instance

#### Methods

##### `initialize_driver()`

```python
def initialize_driver(self, browser_type: str = "chrome") -> WebDriver
```

**Purpose**: Initialize and configure WebDriver instance.

**Parameters**:
- `browser_type`: Browser type ('chrome' or 'firefox')

**Returns**: WebDriver instance

##### `close_driver()`

```python
def close_driver(self) -> None
```

**Purpose**: Safely close WebDriver instance and cleanup resources.

## Agent System

### 1. Orchestrator (`src/agents/orchestrator.py`)

**Purpose**: Global coordination and multi-account management.

#### Class: `AgentOrchestrator`

```python
class AgentOrchestrator:
    def __init__(self, config_loader: ConfigLoader)
```

#### Methods

##### `add_goal()`

```python
async def add_goal(self, account_id: str, goal_description: str, context: Optional[Dict] = None) -> bool
```

**Purpose**: Parse natural language goal and create structured objective.

**Parameters**:
- `account_id`: Target account identifier
- `goal_description`: Natural language goal description
- `context`: Optional additional context

**Returns**: True if goal created successfully

**Example**:
```python
orchestrator = AgentOrchestrator(config_loader)
success = await orchestrator.add_goal(
    "username",
    "Increase engagement rate to 5% and gain 1000 followers in 30 days"
)
```

##### `run_single_cycle()`

```python
async def run_single_cycle(self, account_id: Optional[str] = None) -> None
```

**Purpose**: Execute one complete automation cycle.

**Parameters**:
- `account_id`: Optional specific account, if None runs for all accounts

##### `run_continuous_mode()`

```python
async def run_continuous_mode(self) -> None
```

**Purpose**: Start continuous automation with configurable intervals.

**Long-running Process**: Runs until interrupted or stopped.

##### `get_system_status()`

```python
def get_system_status(self) -> Dict[str, Any]
```

**Purpose**: Retrieve comprehensive system status information.

**Returns**: Dictionary containing system metrics and account status

### 2. Core Agent (`src/agents/core_agent.py`)

**Purpose**: Individual account intelligence and task management.

#### Class: `TwitterAgentCore`

```python
class TwitterAgentCore:
    def __init__(self, config_loader: ConfigLoader, llm_service: LLMService)
```

#### Methods

##### `set_goal()`

```python
async def set_goal(
    self,
    account_id: str,
    goal_description: str,
    target_metrics: Dict[str, Union[int, float]],
    deadline: Optional[datetime] = None,
    priority: TaskPriority = TaskPriority.MEDIUM
) -> AgentGoal
```

**Purpose**: Create and track structured goal for account.

**Parameters**:
- `account_id`: Target account identifier
- `goal_description`: Goal description
- `target_metrics`: Quantifiable metrics (followers, engagement_rate, etc.)
- `deadline`: Optional completion deadline
- `priority`: Goal priority level

**Returns**: Created AgentGoal object

##### `analyze_situation()`

```python
async def analyze_situation(self, account_id: str) -> Dict[str, Any]
```

**Purpose**: Analyze current account situation and performance.

**Parameters**:
- `account_id`: Account to analyze

**Returns**: Situation analysis dictionary

##### `make_decisions()`

```python
async def make_decisions(self, account_id: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]
```

**Purpose**: Make strategic decisions based on situation analysis.

**Parameters**:
- `account_id`: Account for decision making
- `analysis`: Situation analysis results

**Returns**: List of decision objects

##### `plan_for_goal()`

```python
async def plan_for_goal(self, account_id: str, goal: AgentGoal) -> None
```

**Purpose**: Generate strategic task plan to achieve goal.

**Parameters**:
- `account_id`: Target account
- `goal`: Goal to plan for

### 3. Specialized Agents (`src/agents/specialized_agents.py`)

**Purpose**: Task-specific automation capabilities.

#### Base Class: `BaseSpecializedAgent`

```python
class BaseSpecializedAgent(ABC):
    def __init__(self, role: AgentRole, llm_service: LLMService, browser_manager: Optional[BrowserManager] = None)
```

**Abstract Methods**:

##### `can_handle_task()`

```python
@abstractmethod
def can_handle_task(self, task: Any) -> bool
```

**Purpose**: Determine if agent can handle specific task type.

##### `execute_task()`

```python
@abstractmethod
async def execute_task(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]
```

**Purpose**: Execute assigned task with given configuration.

#### Specialized Agent Classes

##### `ContentCreatorAgent`

**Purpose**: Original content generation and creation.

**Capabilities**:
- Tweet composition
- Thread creation
- Reply writing
- Content personalization

**Task Types**:
- `create_original_tweet`
- `create_thread`
- `write_reply`

##### `ContentCuratorAgent`

**Purpose**: Content discovery and curation.

**Capabilities**:
- Industry content sourcing
- Trend monitoring
- Competitor analysis
- Content sharing

**Task Types**:
- `curate_content`
- `share_curated_content`
- `monitor_trends`

##### `EngagementManagerAgent`

**Purpose**: Community interaction and engagement.

**Capabilities**:
- Follower engagement
- Reply management
- Conversation initiation
- Relationship building

**Task Types**:
- `engage_with_followers`
- `manage_replies`
- `respond_to_mentions`

##### `PerformanceAnalystAgent`

**Purpose**: Analytics and performance optimization.

**Capabilities**:
- Metrics tracking
- Performance analysis
- Strategy optimization
- Reporting

**Task Types**:
- `analyze_performance`
- `track_metrics`
- `generate_report`
- `optimize_strategy`

## Data Models

### 1. Core Data Models (`src/data_models.py`)

#### `AccountConfig`

```python
@dataclass
class AccountConfig:
    account_id: str
    username: str
    display_name: str
    bio: Optional[str]
    target_keywords: List[str]
    competitor_profiles: List[str]
    personality_prompt: str
```

**Purpose**: Account-specific configuration and metadata.

#### `AgentGoal`

```python
@dataclass
class AgentGoal:
    id: str
    description: str
    target_metrics: Dict[str, Union[int, float]]
    deadline: Optional[datetime]
    priority: TaskPriority
    progress: float = 0.0
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
```

**Purpose**: Structured goal representation with tracking.

#### `AgentTask`

```python
@dataclass
class AgentTask:
    id: str
    goal_id: str
    role: AgentRole
    description: str
    parameters: Dict[str, Any]
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    scheduled_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
```

**Purpose**: Task definition and execution tracking.

#### `TweetContent`

```python
@dataclass
class TweetContent:
    text: str
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    reply_to: Optional[str] = None
    thread_position: Optional[int] = None
```

**Purpose**: Tweet content structure and metadata.

#### `ScrapedTweet`

```python
@dataclass
class ScrapedTweet:
    tweet_id: str
    author: str
    content: str
    timestamp: datetime
    likes: int
    retweets: int
    replies: int
    url: str
```

**Purpose**: Scraped tweet data structure.

### 2. Enumerations

#### `AgentRole`

```python
class AgentRole(str, Enum):
    STRATEGIST = "strategist"
    CONTENT_CURATOR = "content_curator"
    ENGAGEMENT_MANAGER = "engagement_manager"
    PERFORMANCE_ANALYST = "performance_analyst"
    CONTENT_CREATOR = "content_creator"
```

#### `TaskPriority`

```python
class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

#### `TaskStatus`

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

## Memory Management

### 1. Memory Manager (`src/agents/memory_manager.py`)

**Purpose**: Persistent storage and learning system.

#### Class: `AgentMemoryManager`

```python
class AgentMemoryManager:
    def __init__(self, config_loader: ConfigLoader)
```

#### Methods

##### `save_agent_context()`

```python
async def save_agent_context(self, account_id: str, context: AgentContext) -> None
```

**Purpose**: Persist agent context and state.

**Parameters**:
- `account_id`: Account identifier
- `context`: Agent context to save

##### `load_agent_context()`

```python
async def load_agent_context(self, account_id: str, account_config: AccountConfig) -> Optional[AgentContext]
```

**Purpose**: Load previously saved agent context.

**Parameters**:
- `account_id`: Account identifier
- `account_config`: Account configuration

**Returns**: Loaded AgentContext or None if not found

##### `save_goal_history()`

```python
async def save_goal_history(self, account_id: str, goal: AgentGoal) -> None
```

**Purpose**: Record goal history for learning and tracking.

##### `save_performance_metrics()`

```python
async def save_performance_metrics(self, account_id: str, metrics: Dict[str, Any]) -> None
```

**Purpose**: Store performance metrics for analysis.

## Utility Functions

### 1. Helper Functions

#### JSON Response Cleaning

```python
def _clean_json_response(self, response: str) -> str
```

**Purpose**: Clean LLM responses that may contain markdown formatting.

**Used in**: All agent classes for JSON parsing

**Example**:
```python
# Input: "```json\n{\"key\": \"value\"}\n```"
# Output: "{\"key\": \"value\"}"
cleaned = self._clean_json_response(llm_response)
parsed = json.loads(cleaned)
```

## Error Handling

### Exception Types

#### `LLMServiceError`

```python
class LLMServiceError(Exception):
    """Raised when all LLM services fail"""
    pass
```

#### `ConfigurationError`

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass
```

#### `TaskExecutionError`

```python
class TaskExecutionError(Exception):
    """Raised when task execution fails"""
    pass
```

### Error Response Format

All methods return consistent error information:

```python
{
    "success": False,
    "error": "Description of what went wrong",
    "error_type": "ConfigurationError",
    "timestamp": "2025-08-02T23:45:30.123456",
    "context": {
        "account_id": "username",
        "task_id": "task_123",
        "additional_info": "..."
    }
}
```

## Rate Limiting and Performance

### LLM Service Limits

- **GitHub Copilot**: Automatically managed by httpx client
- **OpenAI**: Built-in rate limiting and retry logic
- **Azure OpenAI**: Respects service quotas
- **Gemini**: Configured timeout and retry handling

### Task Execution Limits

```python
# Configuration in settings.json
{
  "agent_settings": {
    "task_timeout_seconds": 300,
    "max_concurrent_tasks": 3,
    "max_retries": 3
  }
}
```

## Integration Examples

### Basic Usage

```python
import asyncio
from src.core.config_loader import ConfigLoader
from src.agents.orchestrator import AgentOrchestrator

async def main():
    # Initialize system
    config = ConfigLoader()
    orchestrator = AgentOrchestrator(config)
    
    # Add goal
    await orchestrator.add_goal(
        "username",
        "Increase engagement rate to 5% in 30 days"
    )
    
    # Run single cycle
    await orchestrator.run_single_cycle("username")
    
    # Get status
    status = orchestrator.get_system_status()
    print(f"Active goals: {status['total_goals']}")

asyncio.run(main())
```

### Custom Agent Implementation

```python
from src.agents.specialized_agents import BaseSpecializedAgent
from src.agents.core_agent import AgentRole

class CustomAgent(BaseSpecializedAgent):
    def __init__(self, llm_service, browser_manager=None):
        super().__init__(AgentRole.STRATEGIST, llm_service, browser_manager)
    
    def can_handle_task(self, task):
        return task.type in ["custom_task_type"]
    
    async def execute_task(self, task, account_config):
        # Custom task implementation
        return {"success": True, "result": "Custom task completed"}
```

---

*This API reference covers all public interfaces and methods. For internal implementation details, refer to the source code and inline documentation.*
