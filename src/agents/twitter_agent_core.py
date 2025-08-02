"""
Core AI Agent System for Twitter Automation

This module contains the main agent class that enables autonomous
decision-making, planning, and execution of Twitter automation tasks.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import sys
import os

# Import dependencies
from src.core.llm_service import LLMService
from src.core.config_loader import ConfigLoader
from src.data_models import AccountConfig, ScrapedTweet, TweetContent
from .models import (
    AgentRole, TaskPriority, TaskStatus, AgentGoal, 
    AgentTask, AgentMemory, AgentContext
)


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
        self.global_memory = AgentMemory(account_id="global")
        
        # Agent components will be initialized by specialized agents
        self.specialized_agents: Dict[AgentRole, Any] = {}  # Will store BaseSpecializedAgent instances
        
    async def initialize_for_account(self, account_config: AccountConfig) -> AgentContext:
        """Initialize agent context for a specific account"""
        self.logger.info(f"Initializing agent context for account: {account_config.account_id}")
        
        # Create initial memory for this account
        memory = AgentMemory(account_id=account_config.account_id)
        
        # Create agent context
        context = AgentContext(
            account_id=account_config.account_id,
            memory=memory,
            last_activity=datetime.now()
        )
        
        # Store context
        self.contexts[account_config.account_id] = context
        
        self.logger.info(f"Agent context initialized for account: {account_config.account_id}")
        return context
    
    async def add_goal(self, account_id: str, goal_description: str) -> Optional[AgentGoal]:
        """Add a new goal for the agent to work towards"""
        try:
            self.logger.info(f"Adding goal for account {account_id}: {goal_description}")
            
            # Generate goal ID
            goal_id = f"goal_{account_id}_{int(datetime.now().timestamp())}"
            
            # Parse goal using LLM to extract structured information
            goal_data = await self._parse_goal_with_llm(account_id, goal_description)
            
            # Create goal object
            goal = AgentGoal(
                id=goal_id,
                account_id=account_id,
                description=goal_description,
                target_metrics=goal_data.get("target_metrics", {}),
                priority=TaskPriority(goal_data.get("priority", "medium")),
                deadline=goal_data.get("deadline")
            )
            
            # Add to context
            if account_id in self.contexts:
                self.contexts[account_id].current_goals.append(goal)
                self.logger.info(f"Goal added successfully: {goal_id}")
                return goal
            else:
                self.logger.error(f"No context found for account: {account_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error adding goal: {e}")
            return None
    
    async def _parse_goal_with_llm(self, account_id: str, goal_description: str) -> Dict[str, Any]:
        """Use LLM to parse and structure goal information"""
        prompt = f"""
        Parse this goal description for a Twitter automation agent:
        
        Goal: "{goal_description}"
        Account: {account_id}
        
        Extract and return JSON with:
        {{
            "target_metrics": {{
                "followers": number or null,
                "engagement_rate": number or null,
                "posts_per_day": number or null,
                "other_metrics": {{}}
            }},
            "priority": "critical|high|medium|low",
            "timeline_days": number or null,
            "main_actions": ["action1", "action2"],
            "success_criteria": "how to measure success"
        }}
        
        Only return valid JSON, no additional text.
        """
        
        try:
            response = await self.llm_service.generate_text(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            # Clean and parse JSON response
            cleaned_response = self._clean_json_response(response)
            goal_data = json.loads(cleaned_response)
            
            # Convert timeline to deadline if provided
            if goal_data.get("timeline_days"):
                goal_data["deadline"] = datetime.now() + timedelta(days=goal_data["timeline_days"])
            
            return goal_data
            
        except Exception as e:
            self.logger.error(f"Error parsing goal with LLM: {e}")
            return {"priority": "medium", "target_metrics": {}}
    
    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response to extract JSON content"""
        if not response:
            return response
        
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith('```json'):
            response = response.replace('```json', '').replace('```', '').strip()
        elif response.startswith('```'):
            response = response.replace('```', '').strip()
        
        return response
    
    async def plan_actions(self, account_id: str) -> List[AgentTask]:
        """Plan actions to achieve current goals"""
        if account_id not in self.contexts:
            self.logger.error(f"No context found for account: {account_id}")
            return []
        
        context = self.contexts[account_id]
        
        if not context.current_goals:
            self.logger.info(f"No active goals for account: {account_id}")
            return []
        
        try:
            # Generate action plan using LLM
            tasks = await self._generate_action_plan_with_llm(account_id, context)
            
            # Add tasks to context
            context.active_tasks.extend(tasks)
            
            self.logger.info(f"Generated {len(tasks)} tasks for account: {account_id}")
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error planning actions: {e}")
            return []
    
    async def _generate_action_plan_with_llm(self, account_id: str, context: AgentContext) -> List[AgentTask]:
        """Generate action plan using LLM"""
        # Prepare context for LLM
        goals_summary = []
        for goal in context.current_goals:
            goals_summary.append({
                "description": goal.description,
                "priority": goal.priority,
                "target_metrics": goal.target_metrics
            })
        
        prompt = f"""
        Create an action plan for Twitter account {account_id} to achieve these goals:
        
        Goals: {json.dumps(goals_summary, indent=2)}
        
        Recent Performance Score: {context.performance_score}
        
        Generate 3-5 specific, actionable tasks. Return as JSON array:
        [
            {{
                "type": "create_tweet|create_thread|engage_with_users|analyze_performance|curate_content",
                "description": "specific task description",
                "assigned_role": "content_creator|content_curator|engagement_manager|performance_analyst",
                "priority": "critical|high|medium|low",
                "parameters": {{
                    "topic": "optional topic",
                    "style": "optional style",
                    "count": "optional count"
                }}
            }}
        ]
        
        Only return valid JSON array, no additional text.
        """
        
        try:
            response = await self.llm_service.generate_text(
                prompt=prompt,
                max_tokens=600,
                temperature=0.5
            )
            
            # Clean and parse JSON response
            cleaned_response = self._clean_json_response(response)
            tasks_data = json.loads(cleaned_response)
            
            # Convert to AgentTask objects
            tasks = []
            for i, task_data in enumerate(tasks_data):
                task_id = f"task_{account_id}_{int(datetime.now().timestamp())}_{i}"
                
                task = AgentTask(
                    id=task_id,
                    account_id=account_id,
                    goal_id=context.current_goals[0].id if context.current_goals else None,
                    type=task_data.get("type", "create_tweet"),
                    description=task_data.get("description", ""),
                    parameters=task_data.get("parameters", {}),
                    assigned_role=AgentRole(task_data.get("assigned_role", "content_creator")),
                    priority=TaskPriority(task_data.get("priority", "medium"))
                )
                
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error generating action plan with LLM: {e}")
            return []
    
    async def execute_task(self, task: AgentTask, account_config: AccountConfig) -> Dict[str, Any]:
        """Execute a specific task using the appropriate specialized agent"""
        try:
            self.logger.info(f"Executing task {task.id}: {task.type}")
            
            # Find the appropriate specialized agent
            specialized_agent = self.specialized_agents.get(task.assigned_role)
            
            if not specialized_agent:
                self.logger.error(f"No specialized agent found for role: {task.assigned_role}")
                return {"success": False, "error": f"No agent for role {task.assigned_role}"}
            
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            
            # Execute task
            result = await specialized_agent.execute_task(task, account_config)
            
            # Update task with result
            task.result = result
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            task.completed_at = datetime.now()
            
            # Update agent memory
            await specialized_agent.update_memory(task, result)
            
            # Move task to completed
            if task.account_id in self.contexts:
                context = self.contexts[task.account_id]
                if task in context.active_tasks:
                    context.active_tasks.remove(task)
                context.completed_tasks.append(task)
            
            self.logger.info(f"Task {task.id} completed with result: {result.get('success', False)}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            
            # Update task status
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.result = {"success": False, "error": str(e)}
            
            return {"success": False, "error": str(e)}
    
    async def execute_cycle(self, account_id: str) -> Dict[str, Any]:
        """Execute a complete automation cycle for an account"""
        try:
            self.logger.info(f"Starting execution cycle for account: {account_id}")
            
            # Check if we have context for this account
            if account_id not in self.contexts:
                self.logger.error(f"No context found for account: {account_id}")
                return {"success": False, "error": "Account context not found"}
            
            context = self.contexts[account_id]
            cycle_results = []
            
            # Step 1: Analyze current goals and generate tasks
            self.logger.info(f"Analyzing goals for account: {account_id}")
            for goal in context.current_goals:
                if goal.status == "active":
                    # Generate tasks for this goal
                    tasks = await self._generate_tasks_for_goal(account_id, goal)
                    for task in tasks:
                        context.active_tasks.append(task)
                        cycle_results.append(f"Generated task: {task.description}")
            
            # Step 2: Execute high-priority pending tasks
            self.logger.info(f"Executing pending tasks for account: {account_id}")
            executed_tasks = 0
            max_tasks_per_cycle = 3  # Limit tasks per cycle to avoid overwhelming
            
            # Sort tasks by priority
            context.active_tasks.sort(key=lambda t: t.priority.value, reverse=True)
            
            for task in context.active_tasks[:max_tasks_per_cycle]:
                if task.status == TaskStatus.PENDING:
                    result = await self.execute_task(account_id, task.id)
                    cycle_results.append(f"Executed task: {task.description} - Result: {result.get('success', False)}")
                    executed_tasks += 1
            
            # Step 3: Update context and performance
            context.last_activity = datetime.now()
            performance = await self.analyze_performance(account_id)
            
            cycle_summary = {
                "success": True,
                "account_id": account_id,
                "tasks_executed": executed_tasks,
                "goals_active": len([g for g in context.current_goals if g.status == "active"]),
                "tasks_pending": len([t for t in context.active_tasks if t.status == TaskStatus.PENDING]),
                "performance_score": performance.get("success_rate", 0),
                "cycle_results": cycle_results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Cycle completed for account: {account_id} - Tasks executed: {executed_tasks}")
            return cycle_summary
            
        except Exception as e:
            self.logger.error(f"Error in execution cycle for {account_id}: {e}")
            return {"success": False, "error": str(e), "account_id": account_id}
    
    async def _generate_tasks_for_goal(self, account_id: str, goal: AgentGoal) -> List[AgentTask]:
        """Generate specific tasks to work towards a goal"""
        try:
            # Use LLM to generate relevant tasks based on the goal
            prompt = f"""
            Given this goal for Twitter account @{account_id}:
            Goal: {goal.description}
            Target metrics: {goal.target_metrics}
            
            Generate 1-3 specific, actionable tasks that would help achieve this goal.
            Tasks should be realistic and achievable within a day.
            
            Respond with a JSON array of tasks, each with:
            - description: Clear task description
            - priority: high/medium/low
            - estimated_duration: minutes needed
            - task_type: content_creation/engagement/analysis/growth
            
            Example:
            [
                {
                    "description": "Create and post an engaging tweet about AI trends",
                    "priority": "high", 
                    "estimated_duration": 15,
                    "task_type": "content_creation"
                }
            ]
            """
            
            response = await self.llm_service.generate_response(prompt, max_tokens=500)
            
            # Parse the response
            import json
            tasks_data = json.loads(response.strip())
            
            tasks = []
            for task_data in tasks_data:
                task_id = f"task_{account_id}_{int(datetime.now().timestamp() * 1000)}"
                
                task = AgentTask(
                    id=task_id,
                    account_id=account_id,
                    goal_id=goal.id,
                    description=task_data["description"],
                    priority=TaskPriority(task_data.get("priority", "medium")),
                    estimated_duration=task_data.get("estimated_duration", 30),
                    task_type=task_data.get("task_type", "general")
                )
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error generating tasks for goal {goal.id}: {e}")
            # Return a default task if LLM generation fails
            fallback_task = AgentTask(
                id=f"task_{account_id}_{int(datetime.now().timestamp() * 1000)}",
                account_id=account_id,
                goal_id=goal.id,
                description=f"Work towards goal: {goal.description}",
                priority=TaskPriority.MEDIUM,
                estimated_duration=30,
                task_type="general"
            )
            return [fallback_task]
    
    async def analyze_performance(self, account_id: str) -> Dict[str, Any]:
        """Analyze agent performance for an account"""
        if account_id not in self.contexts:
            return {"error": "Account context not found"}
        
        context = self.contexts[account_id]
        
        # Calculate performance metrics
        total_tasks = len(context.completed_tasks)
        successful_tasks = len([t for t in context.completed_tasks if t.result and t.result.get("success")])
        
        performance_data = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "active_goals": len(context.current_goals),
            "performance_score": context.performance_score
        }
        
        # Update context performance score
        context.performance_score = performance_data["success_rate"]
        
        return performance_data
    
    def get_context(self, account_id: str) -> Optional[AgentContext]:
        """Get agent context for an account"""
        return self.contexts.get(account_id)
    
    def get_all_contexts(self) -> Dict[str, AgentContext]:
        """Get all agent contexts"""
        return self.contexts
