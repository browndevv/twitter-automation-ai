"""
Core AI Agent System for Twitter Automation

This module provides backward compatibility imports for the agent system.
The actual implementations have been moved to separate modules for better organization.
"""

# Import all classes from the new modular structure
from .models import (
    AgentRole, TaskPriority, TaskStatus, AgentGoal, 
    AgentTask, AgentMemory, AgentContext
)
from .twitter_agent_core import TwitterAgentCore

# Re-export everything for backward compatibility
__all__ = [
    'AgentRole', 'TaskPriority', 'TaskStatus', 'AgentGoal',
    'AgentTask', 'AgentMemory', 'AgentContext', 'TwitterAgentCore'
]
