"""
Agent Data Models

This module contains data models and enums used by the agent system
including roles, priorities, goals, tasks, and memory structures.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Defines different agent roles for specialized tasks"""
    STRATEGIST = "strategist"  # High-level planning and goal management
    CONTENT_CURATOR = "content_curator"  # Content discovery and curation
    ENGAGEMENT_MANAGER = "engagement_manager"  # Interaction and community management
    PERFORMANCE_ANALYST = "performance_analyst"  # Analytics and optimization
    CONTENT_CREATOR = "content_creator"  # Original content generation


class TaskPriority(str, Enum):
    """Task priority levels for agent scheduling"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentGoal(BaseModel):
    """Represents a high-level goal for the agent system"""
    id: str
    account_id: str
    description: str
    target_metrics: Dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "active"


class AgentTask(BaseModel):
    """Represents a specific task to be executed by an agent"""
    id: str
    account_id: str
    goal_id: Optional[str] = None
    type: str  # Type of task (e.g., "create_tweet", "analyze_performance")
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    assigned_role: AgentRole
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3


class AgentMemory(BaseModel):
    """Represents the agent's memory and learned patterns"""
    account_id: str
    successful_content_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    engagement_insights: Dict[str, Any] = Field(default_factory=dict)
    performance_trends: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)


class AgentContext(BaseModel):
    """Contains the current context and state for an agent working on an account"""
    account_id: str
    current_goals: List[AgentGoal] = Field(default_factory=list)
    active_tasks: List[AgentTask] = Field(default_factory=list)
    completed_tasks: List[AgentTask] = Field(default_factory=list)
    memory: AgentMemory
    last_activity: Optional[datetime] = None
    performance_score: float = 0.0
