# User Guide

## Getting Started

This guide will help you use the Twitter Automation AI system effectively, from initial setup to advanced goal management and monitoring.

## Installation and Setup

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import asyncio, httpx, openai; print('Dependencies installed successfully')"
```

### Step 2: Configure API Keys

1. **Copy configuration template:**
   ```bash
   cp config/settings.json.template config/settings.json
   ```

2. **Add your GitHub Copilot API key:**
   ```json
   {
     "api_keys": {
       "copilot_api_key": "ghu_your_actual_api_key_here"
     }
   }
   ```

3. **Test configuration:**
   ```bash
   python main.py
   ```

### Step 3: Set Up Account Configuration

Edit `config/accounts.json`:

```json
{
  "accounts": {
    "your_username": {
      "username": "your_username",
      "display_name": "Your Display Name",
      "target_keywords": ["your", "keywords", "here"],
      "personality_prompt": "Your brand voice description"
    }
  }
}
```

## Using the Interactive Mode

### Starting the Application

```bash
python main.py
```

You'll see the main menu:

```
==================================================
AGENTIC TWITTER AUTOMATION - INTERACTIVE MODE
==================================================
1. Add new goal
2. Run single cycle (all accounts)
3. Run single cycle (specific account)
4. View system status
5. View account goals
6. View account tasks
7. Start continuous mode
8. Exit
```

### Menu Options Explained

#### 1. Add New Goal

**Purpose**: Create intelligent goals using natural language

**Example Usage**:
```
Enter your goal: I want to increase my engagement rate to 5% and gain 1000 new followers in the next month by posting high-quality AI content daily
```

**What Happens**:
- AI parses your natural language into structured metrics
- Creates specific, actionable tasks
- Sets realistic timelines and priorities
- Generates strategic action plan

**Example Output**:
```
Goal added successfully!
Goal ID: username_1234567890.123456
Description: Increase engagement rate to 5% and gain 1000 followers through daily AI content
Target Metrics: {'followers': 1000, 'engagement_rate': 0.05, 'posts_per_week': 7}
Deadline: 2025-09-02 (30 days)
```

#### 2. Run Single Cycle (All Accounts)

**Purpose**: Execute one complete automation cycle for all configured accounts

**Process**:
1. Analyzes current situation for each account
2. Makes strategic decisions based on goals
3. Executes prioritized tasks
4. Updates performance metrics
5. Provides optimization recommendations

#### 3. Run Single Cycle (Specific Account)

**Purpose**: Focus automation on a single account

**Use Cases**:
- Testing new strategies
- Troubleshooting specific accounts
- Focused optimization

#### 4. View System Status

**Information Displayed**:
- Active accounts and their status
- Total goals across all accounts
- Pending tasks count
- System health metrics

**Example Output**:
```
System Status:
- Running: Yes
- Active Accounts: 2
- Total Goals: 3
- Pending Tasks: 15
- Last Cycle: 2025-08-02 23:45:30
```

#### 5. View Account Goals

**Features**:
- Lists all goals for selected account
- Shows progress percentage
- Displays target metrics and deadlines
- Indicates active/completed status

**Example Output**:
```
Goals for @username:
  ID: username_1754158452.77055
  Description: Increase engagement rate to 5% and gain 1000 followers
  Progress: 15.3%
  Target Metrics: {'followers': 1000, 'engagement_rate': 0.05}
  Deadline: 2025-09-02
  Status: Active
```

#### 6. View Account Tasks

**Task Information**:
- Role-specific tasks (content creation, engagement, analysis)
- Task priorities and status
- Detailed descriptions
- Execution progress

**Example Output**:
```
Tasks for @username:
  ID: username_task_001
  Role: Content Creator
  Description: Create 7 original posts per week focusing on AI insights
  Status: Pending
  Priority: High
  
  ID: username_task_002
  Role: Engagement Manager
  Description: Respond to comments and engage with followers daily
  Status: In Progress
  Priority: High
```

#### 7. Start Continuous Mode

**Purpose**: Automated operation with regular cycles

**Features**:
- Runs indefinitely until stopped (Ctrl+C)
- Configurable cycle intervals (default: 1 minute for testing, 30 minutes for production)
- Real-time progress logging
- Global optimization analysis

**Monitoring Output**:
```
2025-08-02 23:45:30 - INFO - orchestrator - Starting continuous agent execution mode...
2025-08-02 23:45:30 - INFO - orchestrator - Running execution cycle for account: username
2025-08-02 23:45:35 - INFO - llm_service - Successfully generated text using GitHub Copilot
2025-08-02 23:45:40 - INFO - orchestrator - Global optimization analysis completed
2025-08-02 23:45:40 - INFO - orchestrator - Waiting 1.0 minutes until next cycle...
```

## Goal Management

### Natural Language Goal Setting

The system understands various goal formats:

**Growth Goals**:
```
"Grow my followers to 10,000 in 3 months"
"Increase engagement rate to 6% by year end"
"Get 500 new followers this month"
```

**Content Goals**:
```
"Post high-quality content 5 times per week"
"Create viral threads about AI developments"
"Share curated content from industry leaders"
```

**Engagement Goals**:
```
"Improve response time to under 2 hours"
"Increase likes and comments by 50%"
"Build stronger community relationships"
```

**Brand Goals**:
```
"Establish thought leadership in AI space"
"Become recognized expert in automation"
"Build professional network in tech industry"
```

### Goal Components

The AI automatically extracts:

**Target Metrics**:
- `followers`: Specific follower count targets
- `engagement_rate`: Percentage engagement goals (0.01-0.10)
- `posts_per_week`: Content frequency (3-14 posts)
- `reach`: Impression or view targets
- `mentions`: Brand mention objectives

**Deadlines**:
- Parsed from phrases like "in 30 days", "by end of month", "within 3 months"
- Automatic reasonable defaults if not specified

**Priorities**:
- `high`: Urgent, time-sensitive goals
- `medium`: Important, standard timeline
- `low`: Nice-to-have, flexible timing

**Strategy Hints**:
- Content creation suggestions
- Engagement strategies
- Optimization recommendations

### Goal Tracking

**Progress Monitoring**:
- Real-time progress percentage
- Metric achievement tracking
- Timeline adherence analysis
- Performance trend identification

**Automatic Adjustments**:
- Strategy modifications based on performance
- Timeline adjustments for realistic achievement
- Resource reallocation for optimal results

## Task Management

### Task Types by Agent Role

**Strategist Tasks**:
- Content calendar development
- Competitor analysis
- Strategy optimization
- Goal progress review

**Content Creator Tasks**:
- Original tweet composition
- Thread creation
- Visual content planning
- Brand voice consistency

**Content Curator Tasks**:
- Industry content sourcing
- Trend monitoring
- Competitor content analysis
- Hashtag research

**Engagement Manager Tasks**:
- Reply management
- Community interaction
- Follower engagement
- Conversation initiation

**Performance Analyst Tasks**:
- Metrics tracking
- Performance reporting
- Optimization recommendations
- ROI analysis

### Task Execution Flow

1. **Task Creation**: AI generates specific, actionable tasks
2. **Prioritization**: Tasks ranked by importance and urgency
3. **Scheduling**: Optimal timing based on audience and goals
4. **Execution**: Automated or semi-automated task completion
5. **Monitoring**: Real-time progress tracking
6. **Optimization**: Continuous improvement based on results

## Monitoring and Analytics

### Real-Time Monitoring

**Live Logs**:
```bash
# View live logs in terminal
tail -f logs/twitter_automation.log

# Filter for specific components
grep "orchestrator" logs/twitter_automation.log
grep "llm_service" logs/twitter_automation.log
```

**Key Metrics to Watch**:
- Goal progress percentages
- Task completion rates
- LLM service response times
- Error frequencies
- Optimization recommendations

### Performance Dashboard

**Access via Menu Option 4**:
- System health overview
- Account performance summary
- Goal achievement status
- Task execution statistics

### Global Optimization Insights

The system provides strategic recommendations:

**Best Strategies**:
- Successful tactics across accounts
- High-performing content types
- Optimal posting times
- Effective engagement approaches

**Failure Patterns**:
- Common mistakes to avoid
- Underperforming strategies
- Timing issues
- Content gaps

**Opportunities**:
- Growth potential areas
- Untapped audience segments
- Trending topic opportunities
- Competitive advantages

**Resource Allocation**:
- Priority task focus
- Time investment recommendations
- Skill development needs
- Tool and resource suggestions

## Best Practices

### Goal Setting

1. **Be Specific**: Include numbers and timelines
   ```
   Good: "Gain 500 followers in 2 months"
   Poor: "Get more followers"
   ```

2. **Set Realistic Targets**: Based on current performance
   ```
   Current: 1000 followers, 2% engagement
   Realistic: 1500 followers, 3% engagement in 3 months
   Unrealistic: 10000 followers, 10% engagement in 1 month
   ```

3. **Balance Multiple Metrics**: Don't focus on just one aspect
   ```
   Balanced: Growth + engagement + content quality
   Unbalanced: Only follower count
   ```

### Content Strategy

1. **Consistent Voice**: Maintain brand personality across all content
2. **Value-First**: Provide value before promotion
3. **Engagement Focus**: Prioritize meaningful interactions
4. **Quality over Quantity**: Better to post less frequently with higher quality

### Monitoring

1. **Daily Check-ins**: Review progress and adjust strategies
2. **Weekly Analysis**: Deeper dive into performance metrics
3. **Monthly Optimization**: Strategic pivots and goal adjustments
4. **Quarterly Reviews**: Comprehensive strategy evaluation

### Safety and Ethics

1. **Respect Platform Rules**: Follow Twitter's terms of service
2. **Authentic Engagement**: Avoid spam-like behavior
3. **Quality Standards**: Maintain high content standards
4. **Rate Limiting**: Respect API limits and social norms

## Troubleshooting

### Common Issues

**"No LLM services available"**:
- Check API key configuration
- Verify network connectivity
- Review service status

**"Goal parsing failed"**:
- Use more specific language
- Include numeric targets
- Specify timeframes

**"Tasks not executing"**:
- Check task priorities
- Review system resources
- Verify account configurations

**"Poor performance"**:
- Adjust strategy based on analytics
- Modify content approach
- Increase engagement focus

### Getting Help

1. **Check Documentation**: Review relevant guide sections
2. **Review Logs**: Examine error messages and patterns
3. **Validate Configuration**: Ensure all settings are correct
4. **Test Components**: Use single-cycle mode for debugging

## Advanced Usage

### Custom Configurations

1. **Cycle Intervals**: Adjust automation frequency
   ```json
   "agent_settings": {
     "cycle_interval_minutes": 30
   }
   ```

2. **Service Priorities**: Customize LLM service order
   ```json
   "llm_settings": {
     "service_preference_order": ["copilot", "openai"]
   }
   ```

3. **Task Timeouts**: Configure execution limits
   ```json
   "agent_settings": {
     "task_timeout_seconds": 300
   }
   ```

### Multi-Account Management

1. **Account Isolation**: Each account operates independently
2. **Resource Sharing**: Global optimization benefits all accounts
3. **Cross-Account Learning**: Strategies learned from one account benefit others
4. **Coordinated Campaigns**: Synchronized efforts across accounts

### Integration Possibilities

1. **Analytics Platforms**: Export data to external tools
2. **Content Management**: Integration with content creation tools
3. **Social Media Management**: Coordination with other platforms
4. **Business Intelligence**: Connection to enterprise dashboards

---

*This system is designed to grow with your needs. Start simple and gradually explore advanced features as you become more comfortable with the platform.*
