"""
Specialized Agent Classes for Twitter Automation

This module contains specialized agents that handle specific aspects of Twitter automation:
- Content Creation Agent
- Content Curation Agent  
- Engagement Management Agent
- Performance Analysis Agent
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
        
        # Agent state
        self.memory: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.last_action_time: Optional[datetime] = None
        
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


class ContentCuratorAgent(BaseSpecializedAgent):
    """
    Specialized agent for content curation and discovery
    
    Handles:
    - Finding relevant content to share
    - Analyzing trending topics
    - Discovering engagement opportunities
    - Content filtering and selection
    """
    
    def __init__(self, llm_service: LLMService, browser_manager: BrowserManager):
        super().__init__(AgentRole.CONTENT_CURATOR, llm_service, browser_manager)
        self.curated_content = []
        self.trending_topics = []
        
    def can_handle_task(self, task: Any) -> bool:
        """Check if this agent can handle curation tasks"""
        task_types = ["curate_content", "find_trending", "analyze_content", "discover_opportunities"]
        return hasattr(task, 'type') and task.type in task_types
    
    async def execute_task(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Execute content curation task"""
        try:
            self.logger.info(f"Executing curation task: {task.type}")
            
            if task.type == "curate_content":
                return await self._curate_content(task, account_config)
            elif task.type == "find_trending":
                return await self._find_trending_topics(task, account_config)
            elif task.type == "analyze_content":
                return await self._analyze_content(task, account_config)
            elif task.type == "discover_opportunities":
                return await self._discover_opportunities(task, account_config)
            else:
                return {"success": False, "error": f"Unknown task type: {task.type}"}
                
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _curate_content(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Curate relevant content for sharing"""
        niche = task.parameters.get("niche", account_config.niche)
        count = task.parameters.get("count", 5)
        
        # Simulate content discovery
        curated_items = []
        for i in range(count):
            curated_items.append({
                "title": f"Curated content {i+1} for {niche}",
                "url": f"https://example.com/content-{i+1}",
                "relevance_score": 0.8,
                "engagement_potential": 0.7
            })
        
        return {
            "success": True,
            "curated_content": curated_items,
            "action": "content_curated",
            "count": len(curated_items)
        }
    
    async def _find_trending_topics(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Find trending topics in the niche"""
        niche = task.parameters.get("niche", account_config.niche)
        
        # Simulate trending topic discovery
        trending = [
            {"topic": "AI automation", "volume": 1000, "growth": 0.25},
            {"topic": "Machine learning", "volume": 800, "growth": 0.15},
            {"topic": "Python programming", "volume": 600, "growth": 0.30}
        ]
        
        return {
            "success": True,
            "trending_topics": trending,
            "action": "trends_discovered",
            "niche": niche
        }
    
    async def _analyze_content(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Analyze content for relevance and engagement potential"""
        content_url = task.parameters.get("url", "")
        
        # Simulate content analysis
        analysis = {
            "relevance_score": 0.85,
            "engagement_potential": 0.75,
            "sentiment": "positive",
            "key_topics": ["AI", "automation", "productivity"],
            "recommendation": "highly_recommended"
        }
        
        return {
            "success": True,
            "analysis": analysis,
            "action": "content_analyzed",
            "url": content_url
        }
    
    async def _discover_opportunities(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Discover engagement opportunities"""
        # Simulate opportunity discovery
        opportunities = [
            {
                "type": "trending_hashtag",
                "hashtag": "#AIRevolution",
                "potential": 0.8,
                "action": "create_post"
            },
            {
                "type": "viral_thread",
                "url": "https://twitter.com/example/status/123",
                "potential": 0.9,
                "action": "engage_and_reply"
            }
        ]
        
        return {
            "success": True,
            "opportunities": opportunities,
            "action": "opportunities_discovered",
            "count": len(opportunities)
        }


class EngagementManagerAgent(BaseSpecializedAgent):
    """
    Specialized agent for managing engagements and interactions
    
    Handles:
    - Replying to mentions and comments
    - Liking and retweeting relevant content
    - Following relevant accounts
    - Community management
    """
    
    def __init__(self, llm_service: LLMService, browser_manager: BrowserManager):
        super().__init__(AgentRole.ENGAGEMENT_MANAGER, llm_service, browser_manager)
        self.engagement_history = []
        self.interaction_patterns = {}
        
    def can_handle_task(self, task: Any) -> bool:
        """Check if this agent can handle engagement tasks"""
        task_types = ["reply_to_mention", "like_tweets", "retweet_content", "follow_accounts", "engage_community"]
        return hasattr(task, 'type') and task.type in task_types
    
    async def execute_task(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Execute engagement task"""
        try:
            self.logger.info(f"Executing engagement task: {task.type}")
            
            if task.type == "reply_to_mention":
                return await self._reply_to_mention(task, account_config)
            elif task.type == "like_tweets":
                return await self._like_relevant_tweets(task, account_config)
            elif task.type == "retweet_content":
                return await self._retweet_content(task, account_config)
            elif task.type == "follow_accounts":
                return await self._follow_accounts(task, account_config)
            elif task.type == "engage_community":
                return await self._engage_with_community(task, account_config)
            else:
                return {"success": False, "error": f"Unknown task type: {task.type}"}
                
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _reply_to_mention(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Reply to mentions and direct interactions"""
        mention_text = task.parameters.get("mention_text", "")
        author = task.parameters.get("author", "")
        
        prompt = f"""
        Write a thoughtful reply to this mention for @{account_config.username}:
        
        Mention: "{mention_text}"
        From: @{author}
        Brand Voice: {account_config.personality_prompt}
        
        Requirements:
        - Professional and friendly
        - Under 280 characters
        - Adds value to the conversation
        - Maintains brand voice
        
        Return only the reply text.
        """
        
        reply = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=100,
            temperature=0.6
        )
        
        return {
            "success": True,
            "reply": reply,
            "action": "mention_replied",
            "target": author
        }
    
    async def _like_relevant_tweets(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Like tweets that are relevant to the account's interests"""
        count = task.parameters.get("count", 10)
        niche = task.parameters.get("niche", account_config.niche)
        
        # Simulate liking relevant tweets
        liked_tweets = []
        for i in range(count):
            liked_tweets.append({
                "tweet_id": f"tweet_{i+1}",
                "author": f"user_{i+1}",
                "relevance_score": 0.8
            })
        
        return {
            "success": True,
            "liked_tweets": liked_tweets,
            "action": "tweets_liked",
            "count": len(liked_tweets)
        }
    
    async def _retweet_content(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Retweet relevant content with optional commentary"""
        tweet_url = task.parameters.get("tweet_url", "")
        add_comment = task.parameters.get("add_comment", False)
        
        result = {
            "success": True,
            "action": "content_retweeted",
            "tweet_url": tweet_url
        }
        
        if add_comment:
            comment_prompt = f"""
            Write a brief comment to add when retweeting this content for @{account_config.username}.
            
            Brand Voice: {account_config.personality_prompt}
            
            Requirements:
            - Under 100 characters (to leave room for RT)
            - Adds perspective or insight
            - Professional tone
            
            Return only the comment text.
            """
            
            comment = await self.llm_service.generate_text(
                prompt=comment_prompt,
                max_tokens=50,
                temperature=0.6
            )
            
            result["comment"] = comment
        
        return result
    
    async def _follow_accounts(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Follow relevant accounts in the niche"""
        accounts = task.parameters.get("accounts", [])
        
        followed_accounts = []
        for account in accounts[:5]:  # Limit to 5 per task
            followed_accounts.append({
                "username": account,
                "relevance_score": 0.8,
                "followed": True
            })
        
        return {
            "success": True,
            "followed_accounts": followed_accounts,
            "action": "accounts_followed",
            "count": len(followed_accounts)
        }
    
    async def _engage_with_community(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Engage with the broader community through various interactions"""
        engagement_type = task.parameters.get("type", "mixed")
        
        engagements = []
        
        # Simulate various community engagements
        if engagement_type in ["mixed", "replies"]:
            engagements.append({
                "type": "reply",
                "target": "community_post_1",
                "action": "replied_to_discussion"
            })
        
        if engagement_type in ["mixed", "likes"]:
            engagements.append({
                "type": "like",
                "target": "trending_post",
                "action": "liked_relevant_content"
            })
        
        return {
            "success": True,
            "engagements": engagements,
            "action": "community_engaged",
            "count": len(engagements)
        }


class PerformanceAnalystAgent(BaseSpecializedAgent):
    """
    Specialized agent for performance analysis and optimization
    
    Handles:
    - Analyzing tweet performance
    - Tracking follower growth
    - Identifying successful content patterns
    - Providing optimization recommendations
    """
    
    def __init__(self, llm_service: LLMService, browser_manager: Optional[BrowserManager] = None):
        super().__init__(AgentRole.PERFORMANCE_ANALYST, llm_service, browser_manager)
        self.performance_data = {}
        self.analysis_history = []
        
    def can_handle_task(self, task: Any) -> bool:
        """Check if this agent can handle analysis tasks"""
        task_types = ["analyze_performance", "track_metrics", "generate_report", "optimize_strategy"]
        return hasattr(task, 'type') and task.type in task_types
    
    async def execute_task(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Execute performance analysis task"""
        try:
            self.logger.info(f"Executing analysis task: {task.type}")
            
            if task.type == "analyze_performance":
                return await self._analyze_performance_metrics(task, account_config)
            elif task.type == "track_metrics":
                return await self._track_key_metrics(task, account_config)
            elif task.type == "generate_report":
                return await self._generate_performance_report(task, account_config)
            elif task.type == "optimize_strategy":
                return await self._optimize_strategy(task, account_config)
            else:
                return {"success": False, "error": f"Unknown task type: {task.type}"}
                
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_performance_metrics(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Analyze key performance metrics"""
        time_period = task.parameters.get("period", "7days")
        
        # Simulate performance metrics
        metrics = {
            "follower_growth": 15,
            "engagement_rate": 0.045,
            "total_impressions": 5000,
            "total_engagements": 225,
            "best_performing_tweet": {
                "id": "tweet_123",
                "engagements": 50,
                "impressions": 1000
            },
            "optimal_posting_times": ["9:00", "15:00", "20:00"],
            "top_hashtags": ["#AI", "#automation", "#productivity"]
        }
        
        return {
            "success": True,
            "metrics": metrics,
            "action": "performance_analyzed",
            "period": time_period
        }
    
    async def _track_key_metrics(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Track and update key performance indicators"""
        metrics_to_track = task.parameters.get("metrics", ["followers", "engagement", "reach"])
        
        tracked_data = {}
        for metric in metrics_to_track:
            if metric == "followers":
                tracked_data[metric] = {"current": 1250, "change": "+15", "trend": "up"}
            elif metric == "engagement":
                tracked_data[metric] = {"current": 4.5, "change": "+0.3%", "trend": "up"}
            elif metric == "reach":
                tracked_data[metric] = {"current": 5000, "change": "+200", "trend": "up"}
        
        return {
            "success": True,
            "tracked_metrics": tracked_data,
            "action": "metrics_tracked",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_performance_report(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report_type = task.parameters.get("type", "weekly")
        
        # Generate analysis using LLM
        prompt = f"""
        Generate a performance analysis report for Twitter account @{account_config.username}.
        
        Account Niche: {account_config.niche}
        Report Type: {report_type}
        
        Include:
        1. Key performance highlights
        2. Growth trends analysis
        3. Content performance insights
        4. Engagement patterns
        5. Recommendations for improvement
        
        Return as structured JSON with clear sections.
        """
        
        report_content = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.3
        )
        
        return {
            "success": True,
            "report": report_content,
            "action": "report_generated",
            "type": report_type
        }
    
    async def _optimize_strategy(self, task: Any, account_config: AccountConfig) -> Dict[str, Any]:
        """Provide strategy optimization recommendations"""
        focus_area = task.parameters.get("focus", "overall")
        
        # Generate optimization recommendations
        recommendations = {
            "content_strategy": [
                "Increase video content by 20%",
                "Post more during peak hours (9 AM, 3 PM, 8 PM)",
                "Use trending hashtags in AI niche"
            ],
            "engagement_strategy": [
                "Reply to comments within 2 hours",
                "Engage with 10 relevant accounts daily",
                "Share user-generated content weekly"
            ],
            "growth_strategy": [
                "Collaborate with influencers in niche",
                "Create weekly Twitter Spaces",
                "Share valuable resources consistently"
            ]
        }
        
        return {
            "success": True,
            "recommendations": recommendations,
            "action": "strategy_optimized",
            "focus_area": focus_area
        }
