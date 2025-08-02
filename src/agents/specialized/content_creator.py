"""
Content Creator Agent

Specialized agent for creating original content including tweets, threads,
replies, and general content generation with brand voice consistency.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Import dependencies
from src.core.llm_service import LLMService
from src.core.browser_manager import BrowserManager
from src.data_models import AccountConfig
from src.agents.core_agent import AgentRole
from .base_agent import BaseSpecializedAgent


class ContentCreatorAgent(BaseSpecializedAgent):
    """
    Specialized agent for creating original content
    
    Handles:
    - Original tweet composition
    - Thread creation
    - Content personalization
    - Brand voice consistency
    """
    
    def __init__(self, llm_service: LLMService, browser_manager: BrowserManager):
        super().__init__(AgentRole.CONTENT_CREATOR, llm_service, browser_manager)
        self.content_templates = {}
        self.brand_voice_guidelines = {}
        
    def can_handle_task(self, task: Any) -> bool:
        """Check if this agent can handle content creation tasks"""
        task_types = ["create_tweet", "create_thread", "write_reply", "generate_content"]
        return hasattr(task, 'type') and task.type in task_types
    
    async def execute_task(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Execute content creation task"""
        try:
            self.logger.info(f"Executing content creation task: {task.type}")
            
            if task.type == "create_tweet":
                return await self._create_tweet(task, account_config)
            elif task.type == "create_thread":
                return await self._create_thread(task, account_config)
            elif task.type == "write_reply":
                return await self._write_reply(task, account_config)
            elif task.type == "generate_content":
                return await self._generate_content(task, account_config)
            else:
                return {"success": False, "error": f"Unknown task type: {task.type}"}
                
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_tweet(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Create an original tweet"""
        topic = task.parameters.get("topic", "general")
        style = task.parameters.get("style", "professional")
        
        prompt = f"""
        Create an engaging Twitter post for account @{account_config.username}.
        
        Topic: {topic}
        Style: {style}
        Brand Voice: {account_config.personality_prompt}
        
        Requirements:
        - Must be under 280 characters
        - Engaging and authentic
        - Include relevant hashtags (1-3)
        - Match the brand voice
        - Encourage engagement
        
        Return only the tweet text, no additional formatting.
        """
        
        tweet_content = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        # Post the tweet using browser manager
        if self.browser_manager:
            result = await self._post_tweet(tweet_content, account_config)
            return {
                "success": result,
                "content": tweet_content,
                "action": "tweet_posted" if result else "tweet_created"
            }
        else:
            return {
                "success": True,
                "content": tweet_content,
                "action": "tweet_created"
            }
    
    async def _create_thread(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Create a Twitter thread"""
        topic = task.parameters.get("topic", "general")
        length = task.parameters.get("length", 3)
        
        prompt = f"""
        Create a Twitter thread with {length} tweets for @{account_config.username}.
        
        Topic: {topic}
        Brand Voice: {account_config.personality_prompt}
        
        Requirements:
        - Each tweet under 280 characters
        - Coherent narrative flow
        - Engaging opening hook
        - Clear conclusion
        - Include relevant hashtags
        
        Return as JSON array: ["tweet1", "tweet2", "tweet3"]
        """
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7
        )
        
        try:
            cleaned_response = self._clean_json_response(response)
            thread_tweets = json.loads(cleaned_response)
            return {
                "success": True,
                "content": thread_tweets,
                "action": "thread_created",
                "tweet_count": len(thread_tweets)
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse thread response as JSON: {e}")
            self.logger.debug(f"Original response: {response}")
            return {"success": False, "error": "Failed to parse thread response"}
    
    async def _write_reply(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Write a reply to a specific tweet"""
        original_tweet = task.parameters.get("original_tweet", "")
        context = task.parameters.get("context", "")
        
        prompt = f"""
        Write a thoughtful reply to this tweet for @{account_config.username}:
        
        Original Tweet: "{original_tweet}"
        Context: {context}
        Brand Voice: {account_config.personality_prompt}
        
        Requirements:
        - Under 280 characters
        - Adds value to the conversation
        - Authentic and engaging
        - Professional tone
        
        Return only the reply text.
        """
        
        reply_content = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=100,
            temperature=0.6
        )
        
        return {
            "success": True,
            "content": reply_content,
            "action": "reply_created"
        }
    
    async def _generate_content(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Generate general content based on parameters"""
        content_type = task.parameters.get("type", "tweet")
        topic = task.parameters.get("topic", "general")
        
        # Delegate to specific methods based on content type
        if content_type == "tweet":
            return await self._create_tweet(task, account_config)
        elif content_type == "thread":
            return await self._create_thread(task, account_config)
        else:
            return {"success": False, "error": f"Unknown content type: {content_type}"}
    
    async def _post_tweet(self, content: str, account_config: AccountConfig) -> bool:
        """Post a tweet using browser manager"""
        try:
            # This would implement actual tweet posting
            # For now, just simulate success
            await asyncio.sleep(1)  # Simulate posting delay
            self.logger.info(f"Posted tweet: {content[:50]}...")
            return True
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return False
