"""
Core AI Agent System for Twitter Automation

This module contains the main agent architecture that enables autonomous
decision-making, planning, and execution of Twitter automation tasks.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
import sys
import os

# Import dependencies
from src.core.llm_service import LLMService
from src.core.config_loader import ConfigLoader
from src.data_models import AccountConfig, ScrapedTweet, TweetContent


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
    description: str
    target_metrics: Dict[str, Union[int, float]]
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    is_active: bool = True
    progress: float = Field(0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)


class AgentTask(BaseModel):
    """Represents a specific task to be executed by an agent"""
    id: str
    goal_id: Optional[str] = None  # Link to parent goal
    role: AgentRole
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    scheduled_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AgentMemory(BaseModel):
    """Stores agent's memory and learning from past actions"""
    action_history: List[Dict[str, Any]] = Field(default_factory=list)
    successful_strategies: List[Dict[str, Any]] = Field(default_factory=list)
    failed_strategies: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, List[float]] = Field(default_factory=dict)
    learned_patterns: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)


class AgentContext(BaseModel):
    """Current context and state for the agent"""
    account_config: AccountConfig
    current_goals: List[AgentGoal] = Field(default_factory=list)
    active_tasks: List[AgentTask] = Field(default_factory=list)
    memory: AgentMemory = Field(default_factory=AgentMemory)
    environment_state: Dict[str, Any] = Field(default_factory=dict)
    last_action_time: Optional[datetime] = None


class TwitterAgentCore:
    """
    Core AI Agent for Twitter Automation
    
    This agent autonomously plans, decides, and executes Twitter actions
    based on high-level goals and learned strategies.
    """
    
    def __init__(self, config_loader: ConfigLoader, llm_service: LLMService):
        self.config_loader = config_loader
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)
        
        # Agent state
        self.contexts: Dict[str, AgentContext] = {}
        self.global_memory = AgentMemory()
        
        # Agent components will be initialized by specialized agents
        self.specialized_agents: Dict[AgentRole, Any] = {}  # Will store BaseSpecializedAgent instances
        
        # Planning and decision-making settings
        self.planning_interval = timedelta(hours=1)  # How often to re-plan
        self.max_concurrent_tasks = 3
        self.decision_threshold = 0.7  # Confidence threshold for decisions
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean JSON response from LLM to handle markdown formatting
        
        GitHub Copilot and other LLMs sometimes wrap JSON in markdown code blocks
        like ```json ... ``` which breaks JSON parsing.
        """
        if not response:
            return response
            
        # Remove markdown code blocks
        cleaned = response.strip()
        
        # Remove ```json and ``` wrappers
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # Remove ```json
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]   # Remove ```
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # Remove trailing ```
            
        return cleaned.strip()

    async def initialize_for_account(self, account_config: AccountConfig) -> AgentContext:
        """Initialize agent context for a specific account"""
        context = AgentContext(account_config=account_config)
        self.contexts[account_config.account_id] = context
        
        # Load historical memory if available
        await self._load_memory_for_account(account_config.account_id)
        
        self.logger.info(f"Initialized agent context for account: {account_config.account_id}")
        return context

    async def set_goal(self, account_id: str, goal_description: str, 
                      target_metrics: Dict[str, Union[int, float]], 
                      deadline: Optional[datetime] = None) -> AgentGoal:
        """Set a new high-level goal for the agent"""
        goal = AgentGoal(
            id=f"{account_id}_{datetime.now().timestamp()}",
            description=goal_description,
            target_metrics=target_metrics,
            deadline=deadline
        )
        
        context = self.contexts.get(account_id)
        if not context:
            raise ValueError(f"No context found for account: {account_id}")
        
        context.current_goals.append(goal)
        
        # Trigger planning for this new goal
        await self._plan_for_goal(account_id, goal)
        
        self.logger.info(f"Set new goal for {account_id}: {goal_description}")
        return goal

    async def _plan_for_goal(self, account_id: str, goal: AgentGoal):
        """Generate a plan to achieve the specified goal"""
        context = self.contexts[account_id]
        
        # Use LLM to analyze the goal and create a strategy
        planning_prompt = f"""
        You are an AI agent managing a Twitter account. Analyze this goal and create a strategic plan:
        
        Goal: {goal.description}
        Target Metrics: {goal.target_metrics}
        Deadline: {goal.deadline}
        
        Account Context:
        - Keywords: {context.account_config.target_keywords}
        - Competitors: {context.account_config.competitor_profiles}
        - Past Performance: {context.memory.performance_metrics}
        
        Create a list of specific, actionable tasks with priorities and timelines.
        Consider: content creation, curation, engagement, analysis, and optimization.
        
        IMPORTANT: Return ONLY valid JSON array. No explanations or markdown formatting.
        VALID ROLES: content_creator, content_curator, engagement_manager, performance_analyst, strategist
        
        [{{
            "role": "content_creator",
            "description": "specific task description",
            "priority": "high",
            "parameters": {{"key": "value"}},
            "scheduled_time": null
        }}]
        """
        
        try:
            # Get plan from LLM
            response = await self.llm_service.generate_text(
                prompt=planning_prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            # Clean response to extract JSON
            cleaned_response = self._clean_json_response(response)
            
            # Parse and create tasks
            try:
                tasks_data = json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                self.logger.error(f"Failed to parse task planning response as JSON: {json_error}")
                self.logger.debug(f"Original LLM Response was: {response}")
                self.logger.debug(f"Cleaned Response was: {cleaned_response}")
                # Return without creating tasks
                return
            
            for task_data in tasks_data:
                task = AgentTask(
                    id=f"{account_id}_{datetime.now().timestamp()}_{len(context.active_tasks)}",
                    goal_id=goal.id,
                    role=AgentRole(task_data["role"]),
                    description=task_data["description"],
                    priority=TaskPriority(task_data["priority"]),
                    parameters=task_data.get("parameters", {}),
                    scheduled_time=datetime.fromisoformat(task_data["scheduled_time"]) if task_data.get("scheduled_time") else None
                )
                context.active_tasks.append(task)
            
            self.logger.info(f"Created {len(tasks_data)} tasks for goal: {goal.description}")
            
        except Exception as e:
            self.logger.error(f"Failed to plan for goal {goal.id}: {e}")

    async def execute_cycle(self, account_id: str) -> Dict[str, Any]:
        """Execute one cycle of agent decision-making and action"""
        context = self.contexts.get(account_id)
        if not context:
            raise ValueError(f"No context found for account: {account_id}")

        cycle_results = {
            "tasks_executed": 0,
            "decisions_made": 0,
            "actions_taken": [],
            "errors": []
        }

        try:
            # 1. Analyze current situation
            situation_analysis = await self._analyze_situation(account_id)
            
            # 2. Make decisions based on analysis
            decisions = await self._make_decisions(account_id, situation_analysis)
            cycle_results["decisions_made"] = len(decisions)
            
            # 3. Execute highest priority tasks
            executed_tasks = await self._execute_priority_tasks(account_id, decisions)
            cycle_results["tasks_executed"] = len(executed_tasks)
            cycle_results["actions_taken"] = executed_tasks
            
            # 4. Learn from results
            await self._learn_from_cycle(account_id, cycle_results)
            
            # 5. Update context
            context.last_action_time = datetime.now()
            await self._save_memory_for_account(account_id)
            
        except Exception as e:
            error_msg = f"Error in agent cycle for {account_id}: {e}"
            self.logger.error(error_msg)
            cycle_results["errors"].append(error_msg)

        return cycle_results

    async def _analyze_situation(self, account_id: str) -> Dict[str, Any]:
        """Analyze current situation and environment"""
        context = self.contexts[account_id]
        
        analysis_prompt = f"""
        You are analyzing the current situation for a Twitter account to make informed decisions.
        
        Account: {account_id}
        Current Goals: {[g.description for g in context.current_goals if g.is_active]}
        Active Tasks: {len(context.active_tasks)}
        Recent Performance: {context.memory.performance_metrics}
        Last Action: {context.last_action_time}
        
        Environment State: {context.environment_state}
        
        Analyze the situation and provide insights on:
        1. Goal progress and priorities
        2. Opportunities for engagement
        3. Content needs and gaps
        4. Performance trends
        5. Recommended immediate actions
        
        IMPORTANT: Return ONLY valid JSON with these exact keys: goal_progress, opportunities, content_needs, performance_trends, recommendations.
        Do not include any explanations, markdown formatting, or text before/after the JSON.
        
        Example format:
        {{
            "goal_progress": "assessment text",
            "opportunities": "opportunities text", 
            "content_needs": "content needs text",
            "performance_trends": "trends text",
            "recommendations": "recommendations text"
        }}
        """
        
        try:
            response = await self.llm_service.generate_text(
                prompt=analysis_prompt,
                max_tokens=800,
                temperature=0.2
            )
            
            # Clean response to extract JSON
            cleaned_response = self._clean_json_response(response)
            
            if not cleaned_response or not cleaned_response.strip():
                self.logger.warning("Empty response from LLM for situation analysis")
                return {"error": "Empty response from LLM"}
            
            try:
                return json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                self.logger.error(f"Failed to parse situation analysis response as JSON: {json_error}")
                self.logger.debug(f"Original LLM Response was: {response}")
                self.logger.debug(f"Cleaned Response was: {cleaned_response}")
                return {"error": f"JSON parsing error: {json_error}"}
        except Exception as e:
            self.logger.error(f"Failed to analyze situation: {e}")
            return {"error": str(e)}

    async def _make_decisions(self, account_id: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Make decisions based on situation analysis"""
        context = self.contexts[account_id]
        
        decision_prompt = f"""
        Based on the situation analysis, make strategic decisions for immediate actions:
        
        Analysis: {analysis}
        Available Task Types: content_creation, content_curation, engagement, performance_analysis
        Available Roles: content_creator, content_curator, engagement_manager, performance_analyst, strategist
        Current Time: {datetime.now()}
        
        Consider:
        - Goal priorities and deadlines
        - Resource constraints
        - Timing and scheduling
        - Performance optimization opportunities
        
        IMPORTANT: Return ONLY valid JSON array with this exact structure. No explanations or markdown formatting.
        
        [{{
            "action_type": "content_creation",
            "confidence": 0.8,
            "reasoning": "explanation",
            "parameters": {{"key": "value"}},
            "urgency": "high"
        }}]
        """
        
        try:
            response = await self.llm_service.generate_text(
                prompt=decision_prompt,
                max_tokens=600,
                temperature=0.3
            )
            
            # Clean response to extract JSON
            cleaned_response = self._clean_json_response(response)
            
            if not cleaned_response or not cleaned_response.strip():
                self.logger.warning("Empty response from LLM for decision making")
                return []
            
            try:
                decisions = json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                self.logger.error(f"Failed to parse decision response as JSON: {json_error}")
                self.logger.debug(f"Original LLM Response was: {response}")
                self.logger.debug(f"Cleaned Response was: {cleaned_response}")
                return []
            
            # Filter decisions by confidence threshold
            high_confidence_decisions = [
                d for d in decisions 
                if d.get("confidence", 0) >= self.decision_threshold
            ]
            
            return high_confidence_decisions
            
        except Exception as e:
            self.logger.error(f"Failed to make decisions: {e}")
            return []

    async def _execute_priority_tasks(self, account_id: str, decisions: List[Dict[str, Any]]) -> List[str]:
        """Execute the highest priority tasks based on decisions"""
        executed_actions = []
        
        # Sort decisions by urgency and confidence
        sorted_decisions = sorted(
            decisions, 
            key=lambda x: (x.get("urgency") == "high", x.get("confidence", 0)), 
            reverse=True
        )
        
        for decision in sorted_decisions[:self.max_concurrent_tasks]:
            try:
                action_type = decision["action_type"]
                parameters = decision.get("parameters", {})
                
                # Delegate to specialized agents
                if action_type in ["content_creation", "content_curation"]:
                    result = await self._execute_content_action(account_id, action_type, parameters)
                elif action_type == "engagement":
                    result = await self._execute_engagement_action(account_id, parameters)
                elif action_type == "analysis":
                    result = await self._execute_analysis_action(account_id, parameters)
                
                executed_actions.append(f"{action_type}: {result}")
                
            except Exception as e:
                error_msg = f"Failed to execute {decision['action_type']}: {e}"
                self.logger.error(error_msg)
                executed_actions.append(error_msg)

        return executed_actions

    async def _execute_content_action(self, account_id: str, action_type: str, parameters: Dict[str, Any]) -> str:
        """Execute content-related actions"""
        # This will be implemented by specialized content agents
        return f"Content action {action_type} executed with params: {parameters}"

    async def _execute_engagement_action(self, account_id: str, parameters: Dict[str, Any]) -> str:
        """Execute engagement-related actions"""
        # This will be implemented by specialized engagement agents
        return f"Engagement action executed with params: {parameters}"

    async def _execute_analysis_action(self, account_id: str, parameters: Dict[str, Any]) -> str:
        """Execute analysis-related actions"""
        # This will be implemented by specialized analysis agents
        return f"Analysis action executed with params: {parameters}"

    async def _learn_from_cycle(self, account_id: str, cycle_results: Dict[str, Any]):
        """Learn from the results of this execution cycle"""
        context = self.contexts[account_id]
        
        # Record this cycle in memory
        cycle_record = {
            "timestamp": datetime.now().isoformat(),
            "results": cycle_results,
            "context_snapshot": {
                "active_goals": len(context.current_goals),
                "active_tasks": len(context.active_tasks)
            }
        }
        
        context.memory.action_history.append(cycle_record)
        
        # Update performance metrics based on results
        if cycle_results["tasks_executed"] > 0:
            if "execution_rate" not in context.memory.performance_metrics:
                context.memory.performance_metrics["execution_rate"] = []
            context.memory.performance_metrics["execution_rate"].append(cycle_results["tasks_executed"])
        
        # Keep memory manageable by limiting history size
        if len(context.memory.action_history) > 100:
            context.memory.action_history = context.memory.action_history[-100:]

        context.memory.last_updated = datetime.now()

    async def _load_memory_for_account(self, account_id: str):
        """Load historical memory for an account"""
        # Memory loading is now handled by AgentMemoryManager in orchestrator
        pass

    async def _save_memory_for_account(self, account_id: str):
        """Save current memory state for an account"""
        # Memory saving is now handled by AgentMemoryManager in orchestrator
        self.logger.debug(f"Memory operations for {account_id} handled by orchestrator")

    def get_agent_status(self, account_id: str) -> Dict[str, Any]:
        """Get current status of the agent for an account"""
        context = self.contexts.get(account_id)
        if not context:
            return {"error": "Account not found"}

        return {
            "account_id": account_id,
            "active_goals": len([g for g in context.current_goals if g.is_active]),
            "pending_tasks": len([t for t in context.active_tasks if t.status == TaskStatus.PENDING]),
            "last_action": context.last_action_time,
            "memory_size": len(context.memory.action_history),
            "performance_metrics": context.memory.performance_metrics
        }
