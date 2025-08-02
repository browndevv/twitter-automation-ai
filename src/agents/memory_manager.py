"""
Memory and Persistence System for AI Agents

This module handles storing and retrieving agent memory, learning from past actions,
and maintaining state across sessions.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# Import dependencies
from src.core.config_loader import ConfigLoader
from src.agents.core_agent import AgentMemory, AgentGoal, AgentTask, AgentContext


class AgentMemoryManager:
    """Manages persistent storage and retrieval of agent memory"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.logger = logging.getLogger(__name__)
        
        # Create memory storage directory
        self.memory_dir = Path("agent_memory")
        self.memory_dir.mkdir(exist_ok=True)
        
        # Storage paths
        self.contexts_dir = self.memory_dir / "contexts"
        self.goals_dir = self.memory_dir / "goals"
        self.performance_dir = self.memory_dir / "performance"
        
        for dir_path in [self.contexts_dir, self.goals_dir, self.performance_dir]:
            dir_path.mkdir(exist_ok=True)
    
    async def save_agent_context(self, account_id: str, context: AgentContext):
        """Save agent context to persistent storage"""
        try:
            context_file = self.contexts_dir / f"{account_id}_context.json"
            
            # Convert context to serializable format
            context_data = {
                "account_id": account_id,
                "current_goals": [goal.model_dump() for goal in context.current_goals],
                "active_tasks": [task.model_dump() for task in context.active_tasks],
                "completed_tasks": [task.model_dump() for task in context.completed_tasks],
                "memory": {
                    "account_id": context.memory.account_id,
                    "successful_content_patterns": context.memory.successful_content_patterns,
                    "engagement_insights": context.memory.engagement_insights,
                    "performance_trends": context.memory.performance_trends,
                    "last_updated": context.memory.last_updated.isoformat()
                },
                "last_activity": context.last_activity.isoformat() if context.last_activity else None,
                "performance_score": context.performance_score,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved context for account: {account_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save context for {account_id}: {e}")
    
    async def load_agent_context(self, account_id: str, account_config) -> Optional[AgentContext]:
        """Load agent context from persistent storage"""
        try:
            context_file = self.contexts_dir / f"{account_id}_context.json"
            
            if not context_file.exists():
                # Create new context if none exists
                memory = AgentMemory(account_id=account_id)
                return AgentContext(account_id=account_id, memory=memory)
            
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            # Reconstruct context objects
            from .models import AgentGoal, AgentTask, TaskStatus, AgentRole, TaskPriority
            
            # Reconstruct goals
            goals = []
            for goal_data in context_data.get("current_goals", []):
                # Ensure account_id is present in goal data
                if "account_id" not in goal_data:
                    goal_data["account_id"] = account_id
                goal = AgentGoal(**goal_data)
                goals.append(goal)
            
            # Reconstruct tasks  
            tasks = []
            for task_data in context_data.get("active_tasks", []):
                # Ensure account_id is present in task data
                if "account_id" not in task_data:
                    task_data["account_id"] = account_id
                task = AgentTask(**task_data)
                tasks.append(task)
            
            # Reconstruct completed tasks
            completed_tasks = []
            for task_data in context_data.get("completed_tasks", []):
                # Ensure account_id is present in task data
                if "account_id" not in task_data:
                    task_data["account_id"] = account_id
                task = AgentTask(**task_data)
                completed_tasks.append(task)
            
            # Reconstruct memory
            memory_data = context_data.get("memory", {})
            memory = AgentMemory(
                account_id=account_id,
                successful_content_patterns=memory_data.get("successful_content_patterns", []),
                engagement_insights=memory_data.get("engagement_insights", {}),
                performance_trends=memory_data.get("performance_trends", {}),
                last_updated=datetime.fromisoformat(memory_data.get("last_updated", datetime.now().isoformat()))
            )
            
            # Create context
            context = AgentContext(
                account_id=account_id,
                current_goals=goals,
                active_tasks=tasks,
                completed_tasks=completed_tasks,
                memory=memory,
                last_activity=datetime.fromisoformat(context_data["last_activity"]) if context_data.get("last_activity") else None,
                performance_score=context_data.get("performance_score", 0.0)
            )
            
            self.logger.debug(f"Loaded context for account: {account_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to load context for {account_id}: {e}")
            # Return new context on error
            return AgentContext(account_config=account_config)
    
    async def save_goal_history(self, account_id: str, goal: AgentGoal):
        """Save goal to historical record"""
        try:
            goals_file = self.goals_dir / f"{account_id}_goals.json"
            
            # Load existing goals
            goals_history = []
            if goals_file.exists():
                with open(goals_file, 'r', encoding='utf-8') as f:
                    goals_history = json.load(f)
            
            # Add new goal
            goal_record = goal.model_dump()
            goal_record["archived_at"] = datetime.now().isoformat()
            goals_history.append(goal_record)
            
            # Keep only recent goals (last 50)
            goals_history = goals_history[-50:]
            
            # Save updated history
            with open(goals_file, 'w', encoding='utf-8') as f:
                json.dump(goals_history, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved goal history for account: {account_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save goal history for {account_id}: {e}")
    
    async def get_goal_history(self, account_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get goal history for the specified period"""
        try:
            goals_file = self.goals_dir / f"{account_id}_goals.json"
            
            if not goals_file.exists():
                return []
            
            with open(goals_file, 'r', encoding='utf-8') as f:
                goals_history = json.load(f)
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_goals = []
            
            for goal in goals_history:
                goal_date = datetime.fromisoformat(goal.get("created_at", goal.get("archived_at", "1970-01-01")))
                if goal_date >= cutoff_date:
                    recent_goals.append(goal)
            
            return recent_goals
            
        except Exception as e:
            self.logger.error(f"Failed to get goal history for {account_id}: {e}")
            return []
    
    async def save_performance_metrics(self, account_id: str, metrics: Dict[str, Any]):
        """Save performance metrics"""
        try:
            perf_file = self.performance_dir / f"{account_id}_performance.json"
            
            # Load existing metrics
            performance_history = []
            if perf_file.exists():
                with open(perf_file, 'r', encoding='utf-8') as f:
                    performance_history = json.load(f)
            
            # Add new metrics
            metric_record = {
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics
            }
            performance_history.append(metric_record)
            
            # Keep only recent metrics (last 100 records)
            performance_history = performance_history[-100:]
            
            # Save updated history
            with open(perf_file, 'w', encoding='utf-8') as f:
                json.dump(performance_history, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved performance metrics for account: {account_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save performance metrics for {account_id}: {e}")
    
    async def get_performance_trends(self, account_id: str, days: int = 7) -> Dict[str, Any]:
        """Get performance trends for analysis"""
        try:
            perf_file = self.performance_dir / f"{account_id}_performance.json"
            
            if not perf_file.exists():
                return {}
            
            with open(perf_file, 'r', encoding='utf-8') as f:
                performance_history = json.load(f)
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_metrics = []
            
            for record in performance_history:
                record_date = datetime.fromisoformat(record["timestamp"])
                if record_date >= cutoff_date:
                    recent_metrics.append(record)
            
            # Analyze trends
            trends = self._analyze_performance_trends(recent_metrics)
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get performance trends for {account_id}: {e}")
            return {}
    
    def _analyze_performance_trends(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends from historical data"""
        if not metrics_history:
            return {}
        
        trends = {
            "total_records": len(metrics_history),
            "date_range": {
                "start": metrics_history[0]["timestamp"] if metrics_history else None,
                "end": metrics_history[-1]["timestamp"] if metrics_history else None
            },
            "metric_trends": {}
        }
        
        # Aggregate metrics
        metric_sums = {}
        for record in metrics_history:
            for metric_name, value in record.get("metrics", {}).items():
                if isinstance(value, (int, float)):
                    if metric_name not in metric_sums:
                        metric_sums[metric_name] = []
                    metric_sums[metric_name].append(value)
        
        # Calculate trends
        for metric_name, values in metric_sums.items():
            if len(values) >= 2:
                trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
                trends["metric_trends"][metric_name] = {
                    "trend": trend,
                    "latest_value": values[-1],
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values)
                }
        
        return trends
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old memory data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cleaned_files = 0
            
            # Clean up old context files
            for context_file in self.contexts_dir.glob("*_context.json"):
                if context_file.stat().st_mtime < cutoff_date.timestamp():
                    context_file.unlink()
                    cleaned_files += 1
            
            # Clean up old performance files
            for perf_file in self.performance_dir.glob("*_performance.json"):
                try:
                    with open(perf_file, 'r') as f:
                        performance_data = json.load(f)
                    
                    # Filter recent records
                    recent_records = []
                    for record in performance_data:
                        record_date = datetime.fromisoformat(record["timestamp"])
                        if record_date >= cutoff_date:
                            recent_records.append(record)
                    
                    # Save filtered data
                    if recent_records:
                        with open(perf_file, 'w') as f:
                            json.dump(recent_records, f, indent=2)
                    else:
                        perf_file.unlink()
                        cleaned_files += 1
                        
                except Exception:
                    continue
            
            self.logger.info(f"Cleaned up {cleaned_files} old memory files")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memory data"""
        try:
            stats = {
                "contexts": len(list(self.contexts_dir.glob("*_context.json"))),
                "goal_histories": len(list(self.goals_dir.glob("*_goals.json"))),
                "performance_files": len(list(self.performance_dir.glob("*_performance.json"))),
                "total_size_mb": 0
            }
            
            # Calculate total size
            total_size = 0
            for file_path in self.memory_dir.rglob("*.json"):
                total_size += file_path.stat().st_size
            
            stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return {}
