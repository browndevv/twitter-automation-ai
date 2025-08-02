"""
Agent Orchestrator - Coordinates the AI agent system for Twitter automation

This module provides the main interface for running the agentic Twitter automation
system, managing multiple specialized agents and coordinating their activities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import sys
import os

# Import dependencies
from src.core.config_loader import ConfigLoader
from src.core.browser_manager import BrowserManager
from src.core.llm_service import LLMService
from src.data_models import AccountConfig
from src.agents.core_agent import TwitterAgentCore, AgentGoal, TaskPriority
from src.agents.specialized import (
    BaseSpecializedAgent, 
    ContentCreatorAgent, 
    ContentCuratorAgent,
    EngagementManagerAgent, 
    PerformanceAnalystAgent
)
from src.agents.memory_manager import AgentMemoryManager


class AgentOrchestrator:
    """
    Main orchestrator for the AI agent system
    
    Manages multiple accounts, coordinates specialized agents,
    and handles high-level goal processing and execution cycles.
    """
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.llm_service = LLMService(config_loader)
        self.logger = logging.getLogger(__name__)
        
        # Core agent system
        self.core_agent = TwitterAgentCore(config_loader, self.llm_service)
        
        # Memory management
        self.memory_manager = AgentMemoryManager(config_loader)
        
        # Account-specific browser managers and specialized agents
        self.browser_managers: Dict[str, BrowserManager] = {}
        self.specialized_agents: Dict[str, Dict[str, BaseSpecializedAgent]] = {}
        
        # Orchestrator settings
        self.cycle_interval = timedelta(minutes=1)  # How often to run agent cycles (reduced for testing)
        self.max_concurrent_accounts = 3
        self.is_running = False
        
        # Goal processing queue
        self.pending_goals: List[Dict[str, Any]] = []
        
    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response to extract JSON content from markdown or other formatting"""
        if not response:
            return response
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # Handle markdown code blocks
        if response.startswith('```json'):
            response = response.replace('```json', '').replace('```', '').strip()
        elif response.startswith('```'):
            response = response.replace('```', '').strip()
        
        return response
    
    async def initialize(self):
        """Initialize the agent system"""
        self.logger.info("Initializing Agent Orchestrator...")
        
        # Load account configurations
        accounts_data = self.config_loader.get_accounts_config()
        
        for account_dict in accounts_data:
            if not account_dict.get('is_active', True):
                continue
                
            try:
                # Create AccountConfig model
                account_config = AccountConfig.model_validate(account_dict)
                
                # Initialize core agent context for this account
                context = await self.core_agent.initialize_for_account(account_config)
                
                # Load historical context from memory
                saved_context = await self.memory_manager.load_agent_context(account_config.account_id, account_config)
                if saved_context:
                    # Merge saved context with new context
                    context.memory = saved_context.memory
                    context.current_goals = saved_context.current_goals
                    context.active_tasks = saved_context.active_tasks
                    context.completed_tasks = saved_context.completed_tasks
                    context.last_activity = saved_context.last_activity
                    context.performance_score = saved_context.performance_score
                    self.core_agent.contexts[account_config.account_id] = context
                
                # Initialize browser manager for this account
                browser_manager = BrowserManager(account_config=account_dict)
                self.browser_managers[account_config.account_id] = browser_manager
                
                # Initialize specialized agents for this account
                await self._initialize_specialized_agents_for_account(account_config.account_id, browser_manager)
                
                self.logger.info(f"Initialized agent system for account: {account_config.account_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize account {account_dict.get('account_id', 'Unknown')}: {e}")
        
        self.logger.info("Agent Orchestrator initialization complete")
    
    async def _initialize_specialized_agents_for_account(self, account_id: str, browser_manager: BrowserManager):
        """Initialize specialized agents for a specific account"""
        agents = {}
        
        # Initialize all specialized agents
        agents['content_creator'] = ContentCreatorAgent(self.llm_service, browser_manager)
        agents['content_curator'] = ContentCuratorAgent(self.llm_service, browser_manager)
        agents['engagement_manager'] = EngagementManagerAgent(self.llm_service, browser_manager)
        agents['performance_analyst'] = PerformanceAnalystAgent(self.llm_service)
        
        self.specialized_agents[account_id] = agents
        
        # Register with core agent
        for agent in agents.values():
            self.core_agent.specialized_agents[agent.role] = agent
    
    async def add_goal_from_natural_language(self, account_id: str, goal_description: str, 
                                           context: Optional[Dict[str, Any]] = None) -> AgentGoal:
        """
        Add a goal using natural language input
        
        Examples:
        - "Grow followers in AI niche by 500 in the next month"
        - "Increase engagement rate to 5% within 2 weeks"
        - "Become a thought leader in machine learning"
        """
        
        # Use LLM to parse the natural language goal into structured format
        parsing_prompt = f"""
        Parse this natural language goal into structured format for a Twitter automation agent:
        
        Goal: "{goal_description}"
        Account Context: {context or {}}
        
        Return ONLY valid JSON without any markdown formatting or code blocks:
        {{
            "parsed_goal": "clear, specific goal description",
            "target_metrics": {{"followers": 1500, "engagement_rate": 0.05, "posts_per_week": 5}},
            "deadline_days": 30,
            "priority": "high",
            "strategy_hints": ["post consistently", "engage with followers"],
            "success_criteria": ["reach follower target", "maintain engagement rate"]
        }}
        
        IMPORTANT: 
        - target_metrics must contain NUMERIC values only (integers or decimals)
        - Use realistic numbers: followers (100-10000), engagement_rate (0.01-0.10), posts_per_week (3-14)
        - deadline_days should be a number (7, 14, 30, 60, 90) or null
        """
        
        try:
            response = await self.llm_service.generate_text(
                prompt=parsing_prompt,
                max_tokens=300,
                temperature=0.2
            )
            
            if not response or not response.strip():
                self.logger.warning("Empty response from LLM for goal parsing")
                # Fallback to basic goal creation
                return await self.core_agent.set_goal(
                    account_id=account_id,
                    goal_description=goal_description,
                    target_metrics={"general_progress": 1.0}
                )
            
            # Clean the response to handle markdown formatting
            cleaned_response = self._clean_json_response(response)
            
            try:
                parsed_goal = json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                self.logger.error(f"Failed to parse goal response as JSON: {json_error}")
                self.logger.debug(f"Original LLM Response was: {response}")
                self.logger.debug(f"Cleaned Response was: {cleaned_response}")
                # Fallback to basic goal creation
                return await self.core_agent.set_goal(
                    account_id=account_id,
                    goal_description=goal_description,
                    target_metrics={"general_progress": 1.0}
                )
            
            # Calculate deadline if specified
            deadline = None
            if parsed_goal.get("deadline_days"):
                deadline = datetime.now() + timedelta(days=parsed_goal["deadline_days"])
            
            # Create and set the goal
            goal = await self.core_agent.set_goal(
                account_id=account_id,
                goal_description=parsed_goal["parsed_goal"],
                target_metrics=parsed_goal["target_metrics"],
                deadline=deadline
            )
            
            # Store additional context
            goal_context = {
                "original_input": goal_description,
                "strategy_hints": parsed_goal.get("strategy_hints", []),
                "success_criteria": parsed_goal.get("success_criteria", [])
            }
            
            self.pending_goals.append({
                "goal_id": goal.id,
                "account_id": account_id,
                "context": goal_context
            })
            
            self.logger.info(f"Added goal for {account_id}: {parsed_goal['parsed_goal']}")
            return goal
            
        except Exception as e:
            self.logger.error(f"Failed to parse goal '{goal_description}': {e}")
            # Fallback to basic goal creation
            return await self.core_agent.set_goal(
                account_id=account_id,
                goal_description=goal_description,
                target_metrics={"general_progress": 1.0}
            )
    
    async def run_continuous_mode(self):
        """Run the agent system continuously"""
        self.is_running = True
        self.logger.info("Starting continuous agent execution mode...")
        
        try:
            while self.is_running:
                # Run execution cycles for all active accounts
                await self._run_execution_cycles()
                
                # Process any pending goal updates
                await self._process_pending_goals()
                
                # Perform cross-account analysis and optimization
                await self._perform_global_optimization()
                
                # Wait for next cycle with progress logging
                wait_seconds = self.cycle_interval.total_seconds()
                self.logger.info(f"Waiting {wait_seconds/60:.1f} minutes until next cycle...")
                await asyncio.sleep(wait_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, stopping agent system...")
        except Exception as e:
            self.logger.error(f"Error in continuous mode: {e}")
        finally:
            await self.stop()
    
    async def run_single_cycle(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Run a single execution cycle for one or all accounts"""
        results = {}
        
        accounts_to_process = [account_id] if account_id else list(self.core_agent.contexts.keys())
        
        for acc_id in accounts_to_process:
            if acc_id not in self.core_agent.contexts:
                self.logger.warning(f"No context found for account: {acc_id}")
                continue
            
            try:
                self.logger.info(f"Running execution cycle for account: {acc_id}")
                cycle_result = await self.core_agent.execute_cycle(acc_id)
                results[acc_id] = cycle_result
                
                # Execute specialized agent tasks based on decisions
                await self._execute_specialized_tasks(acc_id, cycle_result)
                
                # Save updated context and performance metrics
                context = self.core_agent.contexts[acc_id]
                await self.memory_manager.save_agent_context(acc_id, context)
                
                # Save performance metrics
                performance_metrics = {
                    "tasks_executed": cycle_result.get("tasks_executed", 0),
                    "decisions_made": cycle_result.get("decisions_made", 0),
                    "execution_success_rate": 1.0 if not cycle_result.get("errors") else 0.5,
                    "actions_taken": len(cycle_result.get("actions_taken", []))
                }
                await self.memory_manager.save_performance_metrics(acc_id, performance_metrics)
                
            except Exception as e:
                self.logger.error(f"Error in cycle for {acc_id}: {e}")
                results[acc_id] = {"error": str(e)}
        
        return results
    
    async def _run_execution_cycles(self):
        """Run execution cycles for all active accounts"""
        active_accounts = list(self.core_agent.contexts.keys())
        
        # Process accounts in batches to respect concurrency limits
        for i in range(0, len(active_accounts), self.max_concurrent_accounts):
            batch = active_accounts[i:i + self.max_concurrent_accounts]
            
            # Run cycles concurrently for this batch
            tasks = [self.run_single_cycle(account_id) for account_id in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log batch results
            for account_id, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Exception in cycle for {account_id}: {result}")
                else:
                    self.logger.debug(f"Cycle completed for {account_id}: {result}")
    
    async def _execute_specialized_tasks(self, account_id: str, cycle_result: Dict[str, Any]):
        """Execute tasks using specialized agents based on cycle decisions"""
        if account_id not in self.specialized_agents:
            return
        
        agents = self.specialized_agents[account_id]
        context = self.core_agent.contexts[account_id]
        
        # Find pending tasks that can be executed by specialized agents
        for task in context.active_tasks:
            if task.status.value != "pending":
                continue
            
            # Find the appropriate specialized agent
            agent = None
            if task.role.value == "content_creator":
                agent = agents.get("content_creator")
            elif task.role.value == "content_curator":
                agent = agents.get("content_curator")
            elif task.role.value == "engagement_manager":
                agent = agents.get("engagement_manager")
            elif task.role.value == "performance_analyst":
                agent = agents.get("performance_analyst")
            
            if agent and agent.can_handle_task(task):
                try:
                    # Execute the task
                    task.status = "in_progress"
                    result = await agent.execute_task(task, context.account_config)
                    
                    # Update task status and result
                    if result.get("success"):
                        task.status = "completed"
                        task.result = result
                    else:
                        task.status = "failed"
                        task.error_message = result.get("error", "Unknown error")
                    
                    # Update agent memory
                    await agent.update_memory(task, result)
                    
                    self.logger.info(f"Completed task {task.id} for {account_id}")
                    
                except Exception as e:
                    task.status = "failed"
                    task.error_message = str(e)
                    self.logger.error(f"Failed to execute task {task.id}: {e}")
    
    async def _process_pending_goals(self):
        """Process any pending goal updates or modifications"""
        for goal_info in self.pending_goals[:]:  # Copy list to allow modification
            try:
                # Check if goal needs updates or has been completed
                goal_id = goal_info["goal_id"]
                account_id = goal_info["account_id"]
                
                context = self.core_agent.contexts.get(account_id)
                if not context:
                    continue
                
                # Find the goal and check its progress
                goal = next((g for g in context.current_goals if g.id == goal_id), None)
                if goal and goal.progress >= 1.0:
                    # Goal completed, remove from pending
                    self.pending_goals.remove(goal_info)
                    self.logger.info(f"Goal completed for {account_id}: {goal.description}")
                
            except Exception as e:
                self.logger.error(f"Error processing pending goal: {e}")
    
    async def _perform_global_optimization(self):
        """Perform cross-account analysis and optimization"""
        try:
            # Analyze performance across all accounts
            all_performance = {}
            
            for account_id, agents in self.specialized_agents.items():
                context = self.core_agent.contexts.get(account_id)
                if not context:
                    continue
                
                account_performance = {}
                for agent_type, agent in agents.items():
                    perf = await agent.analyze_performance(context.account_config)
                    account_performance[agent_type] = perf
                
                all_performance[account_id] = account_performance
            
            # Use LLM to analyze global performance and suggest optimizations
            optimization_prompt = f"""
            Analyze the performance data across multiple Twitter accounts and suggest optimizations:
            
            Performance Data: {json.dumps(all_performance, indent=2)}
            
            Provide insights on:
            1. Best performing strategies across accounts
            2. Common failure patterns to avoid
            3. Optimization opportunities
            4. Resource allocation suggestions
            
            IMPORTANT: Return ONLY a valid JSON object with recommendations for each account. 
            Do not include any markdown formatting, explanations, or code blocks.
            Use this exact structure:
            {{
                "account_id": {{
                    "best_strategies": ["strategy1", "strategy2"],
                    "failure_patterns": ["pattern1", "pattern2"],
                    "opportunities": ["opp1", "opp2"],
                    "resource_allocation": ["suggestion1", "suggestion2"]
                }}
            }}
            """
            
            response = await self.llm_service.generate_text(
                prompt=optimization_prompt,
                max_tokens=800,
                temperature=0.2
            )
            
            if not response or not response.strip():
                self.logger.warning("Empty response from LLM for global optimization analysis")
                return
            
            # Clean the response to handle markdown formatting
            cleaned_response = self._clean_json_response(response)
            
            try:
                optimizations = json.loads(cleaned_response)
            except json.JSONDecodeError as json_error:
                self.logger.error(f"Failed to parse LLM response as JSON: {json_error}")
                self.logger.debug(f"Original LLM Response was: {response}")
                self.logger.debug(f"Cleaned Response was: {cleaned_response}")
                # Fallback: just log the raw response
                self.logger.info(f"Global optimization analysis (raw response): {response}")
                return
            
            self.logger.info("Global optimization analysis completed")
            
            # Apply optimizations (this would be implemented based on specific needs)
            # For now, just log the recommendations
            for account_id, recommendations in optimizations.items():
                self.logger.info(f"Optimizations for {account_id}: {recommendations}")
            
        except Exception as e:
            self.logger.error(f"Error in global optimization: {e}")
    
    async def stop(self):
        """Stop the agent system and cleanup resources"""
        self.is_running = False
        self.logger.info("Stopping agent system...")
        
        # Close browser managers
        for browser_manager in self.browser_managers.values():
            try:
                browser_manager.close_driver()
            except Exception as e:
                self.logger.error(f"Error closing browser manager: {e}")
        
        self.logger.info("Agent system stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status = {
            "is_running": self.is_running,
            "active_accounts": len(self.core_agent.contexts),
            "total_goals": sum(len(ctx.current_goals) for ctx in self.core_agent.contexts.values()),
            "pending_tasks": sum(len(ctx.active_tasks) for ctx in self.core_agent.contexts.values()),
            "accounts": {}
        }
        
        for account_id in self.core_agent.contexts.keys():
            account_status = self.core_agent.get_agent_status(account_id)
            status["accounts"][account_id] = account_status
        
        return status
    
    def get_account_goals(self, account_id: str) -> List[Dict[str, Any]]:
        """Get all goals for a specific account"""
        context = self.core_agent.contexts.get(account_id)
        if not context:
            return []
        
        return [goal.model_dump() for goal in context.current_goals]
    
    def get_account_tasks(self, account_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific account"""
        context = self.core_agent.contexts.get(account_id)
        if not context:
            return []
        
        return [task.model_dump() for task in context.active_tasks]
