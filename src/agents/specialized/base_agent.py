"""
Base Specialized Agent Class

This module contains the base class for all specialized agents
that handle specific aspects of Twitter automation.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from enum import Enum
import sys
import os

# Import dependencies
from src.core.llm_service import LLMService
from src.core.browser_manager import BrowserManager
from src.data_models import AccountConfig, ScrapedTweet, TweetContent
from src.agents.core_agent import AgentRole, TaskPriority


class BaseSpecializedAgent(ABC):
    """
    Base class for all specialized agents
    
    Provides common functionality and interface for specialized agents
    that handle specific aspects of Twitter automation.
    """
    
    def __init__(self, role: AgentRole, llm_service: LLMService, browser_manager: Optional[BrowserManager] = None):
        self.role = role
        self.llm_service = llm_service
        self.browser_manager = browser_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize memory and performance tracking
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, float] = {}
    
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
        
    @abstractmethod
    async def execute_task(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Execute a specific task assigned to this agent"""
        pass
    
    @abstractmethod
    def can_handle_task(self, task: Any) -> bool:
        """Check if this agent can handle the given task"""
        pass
    
    async def update_memory(self, task: Any, result: Dict[str, Any]):
        """Update agent memory with task execution results"""
        memory_key = f"task_{task.id}_{datetime.now().isoformat()}"
        self.memory[memory_key] = {
            "task_type": task.type,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False)
        }
        
        # Keep only recent memories (last 100 entries)
        if len(self.memory) > 100:
            oldest_keys = sorted(self.memory.keys())[:len(self.memory) - 100]
            for key in oldest_keys:
                del self.memory[key]
    
    async def analyze_performance(self, account_config: AccountConfig) -> Dict[str, float]:
        """Analyze this agent's performance metrics"""
        if not self.memory:
            return {"success_rate": 0.0, "tasks_completed": 0.0}
        
        successful_tasks = sum(1 for entry in self.memory.values() if entry.get("success", False))
        total_tasks = len(self.memory)
        
        return {
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0.0,
            "tasks_completed": float(total_tasks),
            "avg_performance": sum(self.performance_metrics.values()) / len(self.performance_metrics) if self.performance_metrics else 0.0
        }
