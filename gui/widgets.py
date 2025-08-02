"""
Custom Widgets and Components for Twitter Automation AI GUI

This module contains custom widgets and styling components for a modern,
professional GUI interface.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any
from datetime import datetime


class ModernCard(ctk.CTkFrame):
    """A modern card-style widget for displaying information"""
    
    def __init__(self, parent, title: str, value: str, subtitle: str = "", 
                 color: str = "blue", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.color = color
        
        self.setup_card()
        
    def setup_card(self):
        """Setup the card layout"""
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="gray70"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=self.value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.color
        )
        self.value_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        # Subtitle
        if self.subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=self.subtitle,
                font=ctk.CTkFont(size=10),
                text_color="gray60"
            )
            subtitle_label.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")
    
    def update_value(self, new_value: str, new_subtitle: str = None):
        """Update the card value and optional subtitle"""
        self.value_label.configure(text=new_value)
        if new_subtitle is not None:
            self.subtitle = new_subtitle


class StatusIndicator(ctk.CTkFrame):
    """A status indicator widget with color-coded states"""
    
    def __init__(self, parent, initial_status: str = "offline", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status = initial_status
        self.setup_indicator()
        
    def setup_indicator(self):
        """Setup the status indicator"""
        self.grid_columnconfigure(1, weight=1)
        
        # Status dot
        self.dot_label = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=self.get_status_color()
        )
        self.dot_label.grid(row=0, column=0, padx=(15, 5), pady=10)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self,
            text=self.status.title(),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="w")
        
    def get_status_color(self) -> str:
        """Get color for current status"""
        status_colors = {
            "online": "green",
            "offline": "red",
            "running": "blue",
            "paused": "orange",
            "error": "red",
            "warning": "yellow"
        }
        return status_colors.get(self.status.lower(), "gray")
        
    def update_status(self, new_status: str):
        """Update the status"""
        self.status = new_status
        self.dot_label.configure(text_color=self.get_status_color())
        self.status_label.configure(text=new_status.title())


class ProgressCard(ctk.CTkFrame):
    """A card widget showing progress with a progress bar"""
    
    def __init__(self, parent, title: str, current: int, target: int, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.current = current
        self.target = target
        
        self.setup_card()
        
    def setup_card(self):
        """Setup the progress card"""
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Progress info
        progress_text = f"{self.current} / {self.target}"
        percentage = (self.current / self.target * 100) if self.target > 0 else 0
        
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        progress_label = ctk.CTkLabel(
            info_frame,
            text=progress_text,
            font=ctk.CTkFont(size=12)
        )
        progress_label.grid(row=0, column=0, sticky="w")
        
        percentage_label = ctk.CTkLabel(
            info_frame,
            text=f"{percentage:.1f}%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        percentage_label.grid(row=0, column=1, sticky="e")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(percentage / 100)
        
    def update_progress(self, current: int, target: int = None):
        """Update the progress"""
        self.current = current
        if target is not None:
            self.target = target
            
        percentage = (self.current / self.target * 100) if self.target > 0 else 0
        self.progress_bar.set(percentage / 100)


class ActivityFeed(ctk.CTkScrollableFrame):
    """A scrollable activity feed widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.activities = []
        self.setup_feed()
        
    def setup_feed(self):
        """Setup the activity feed"""
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header_label = ctk.CTkLabel(
            self,
            text="Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
    def add_activity(self, message: str, activity_type: str = "info", timestamp: datetime = None):
        """Add a new activity to the feed"""
        if timestamp is None:
            timestamp = datetime.now()
            
        activity_frame = ctk.CTkFrame(self)
        activity_frame.grid(row=len(self.activities) + 1, column=0, padx=20, pady=5, sticky="ew")
        activity_frame.grid_columnconfigure(1, weight=1)
        
        # Activity type icon
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️",
            "task": "📋",
            "goal": "🎯"
        }
        
        icon_label = ctk.CTkLabel(
            activity_frame,
            text=icons.get(activity_type, "ℹ️"),
            font=ctk.CTkFont(size=16)
        )
        icon_label.grid(row=0, column=0, padx=(15, 10), pady=15)
        
        # Activity details
        details_frame = ctk.CTkFrame(activity_frame, fg_color="transparent")
        details_frame.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)
        
        message_label = ctk.CTkLabel(
            details_frame,
            text=message,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left"
        )
        message_label.grid(row=0, column=0, sticky="ew")
        
        time_label = ctk.CTkLabel(
            details_frame,
            text=timestamp.strftime("%H:%M:%S"),
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w"
        )
        time_label.grid(row=1, column=0, sticky="w")
        
        self.activities.append({
            "message": message,
            "type": activity_type,
            "timestamp": timestamp,
            "frame": activity_frame
        })
        
    def clear_activities(self):
        """Clear all activities from the feed"""
        for activity in self.activities:
            activity["frame"].destroy()
        self.activities.clear()


class AccountCard(ctk.CTkFrame):
    """A card widget for displaying account information"""
    
    def __init__(self, parent, account_id: str, is_active: bool = True, 
                 stats: Dict[str, Any] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.account_id = account_id
        self.is_active = is_active
        self.stats = stats or {}
        
        self.setup_card()
        
    def setup_card(self):
        """Setup the account card"""
        self.grid_columnconfigure(1, weight=1)
        
        # Account avatar placeholder
        avatar_frame = ctk.CTkFrame(self, width=60, height=60, corner_radius=30)
        avatar_frame.grid(row=0, column=0, padx=20, pady=20, rowspan=2)
        
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=self.account_id[0].upper(),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Account info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=(0, 20), pady=(20, 5), sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Account name
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"@{self.account_id}",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w")
        
        # Status badge
        status_color = "green" if self.is_active else "red"
        status_text = "Active" if self.is_active else "Inactive"
        
        status_label = ctk.CTkLabel(
            info_frame,
            text=status_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=status_color,
            anchor="e"
        )
        status_label.grid(row=0, column=1, sticky="e")
        
        # Stats
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky="ew")
        
        stats_text = f"Goals: {self.stats.get('goals', 0)} | " \
                    f"Tasks: {self.stats.get('tasks', 0)} | " \
                    f"Success: {self.stats.get('success_rate', 0)}%"
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            anchor="w"
        )
        stats_label.grid(row=0, column=0, sticky="w")


class MetricsDashboard(ctk.CTkFrame):
    """A comprehensive metrics dashboard widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.setup_dashboard()
        
    def setup_dashboard(self):
        """Setup the metrics dashboard"""
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Performance metrics
        self.followers_card = ModernCard(
            self, 
            title="Followers", 
            value="1,234", 
            subtitle="+15 this week",
            color="blue"
        )
        self.followers_card.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.engagement_card = ModernCard(
            self,
            title="Engagement Rate",
            value="4.2%",
            subtitle="+0.3% this week",
            color="green"
        )
        self.engagement_card.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.posts_card = ModernCard(
            self,
            title="Posts This Week",
            value="12",
            subtitle="3 per day average",
            color="orange"
        )
        self.posts_card.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Goal progress
        self.goal_progress = ProgressCard(
            self,
            title="Monthly Goal Progress",
            current=67,
            target=100
        )
        self.goal_progress.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update the dashboard with new metrics"""
        if "followers" in metrics:
            self.followers_card.update_value(str(metrics["followers"]))
        if "engagement_rate" in metrics:
            self.engagement_card.update_value(f"{metrics['engagement_rate']}%")
        if "posts_count" in metrics:
            self.posts_card.update_value(str(metrics["posts_count"]))
        if "goal_progress" in metrics:
            progress = metrics["goal_progress"]
            self.goal_progress.update_progress(progress.get("current", 0), progress.get("target", 100))
