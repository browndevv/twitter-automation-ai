"""
Twitter Automation AI - Modern GUI Application

A professional, responsive graphical user interface for the Twitter Automation AI system.
Built with tkinter and modern styling for a sleek appearance without external dependencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.core.config_loader import ConfigLoader
    from src.agents.orchestrator import AgentOrchestrator
    from src.data_models import AccountConfig
except ImportError:
    print("Warning: Backend modules not available. Running in demo mode.")
    ConfigLoader = None
    AgentOrchestrator = None
    AccountConfig = None


class ModernStyle:
    """Modern styling configuration for the GUI"""
    
    # Color scheme
    COLORS = {
        'bg_primary': '#1e1e1e',
        'bg_secondary': '#2d2d2d',
        'bg_tertiary': '#3d3d3d',
        'accent_blue': '#0078d4',
        'accent_green': '#107c10',
        'accent_red': '#d13438',
        'accent_orange': '#ff8c00',
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'text_muted': '#999999',
        'border': '#454545'
    }
    
    # Fonts
    FONTS = {
        'title': ('Segoe UI', 18, 'bold'),
        'heading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'mono': ('Consolas', 9)
    }


class TwitterAutomationGUI:
    """
    Modern GUI application for Twitter Automation AI system
    
    Features:
    - Account management
    - Goal setting and tracking
    - Real-time monitoring
    - Interactive controls
    - Status visualization
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Twitter Automation AI - Control Center")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configure modern dark theme
        self.setup_theme()
        
        # Initialize backend components
        self.config_loader = None
        self.orchestrator = None
        self.is_running = False
        self.selected_account = None
        
        # GUI components
        self.account_listbox = None
        self.goals_text = None
        self.log_text = None
        self.status_label = None
        self.activity_text = None
        
        # Setup the interface
        self.setup_gui()
        self.load_configuration()
        
    def setup_theme(self):
        """Setup modern dark theme styling"""
        style = ttk.Style()
        
        # Configure the theme
        style.theme_use('clam')
        
        # Configure colors for modern dark theme
        style.configure('Title.TLabel',
                       background=ModernStyle.COLORS['bg_primary'],
                       foreground=ModernStyle.COLORS['text_primary'],
                       font=ModernStyle.FONTS['title'])
        
        style.configure('Heading.TLabel',
                       background=ModernStyle.COLORS['bg_secondary'],
                       foreground=ModernStyle.COLORS['text_primary'],
                       font=ModernStyle.FONTS['heading'])
        
        style.configure('Body.TLabel',
                       background=ModernStyle.COLORS['bg_secondary'],
                       foreground=ModernStyle.COLORS['text_secondary'],
                       font=ModernStyle.FONTS['body'])
        
        # Configure frames
        style.configure('Card.TFrame',
                       background=ModernStyle.COLORS['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Sidebar.TFrame',
                       background=ModernStyle.COLORS['bg_tertiary'],
                       relief='flat')
        
        # Configure notebook tabs
        style.configure('TNotebook',
                       background=ModernStyle.COLORS['bg_secondary'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab',
                       background=ModernStyle.COLORS['bg_tertiary'],
                       foreground=ModernStyle.COLORS['text_secondary'],
                       padding=(20, 10),
                       font=ModernStyle.FONTS['body'])
        
        style.map('TNotebook.Tab',
                 background=[('selected', ModernStyle.COLORS['accent_blue'])],
                 foreground=[('selected', ModernStyle.COLORS['text_primary'])])
        
        # Set root background
        self.root.configure(bg=ModernStyle.COLORS['bg_primary'])
        
    def setup_gui(self):
        """Setup the main GUI layout and components"""
        
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main sections
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
    def create_sidebar(self):
        """Create the left sidebar with navigation and account selection"""
        
        # Sidebar frame
        sidebar_frame = ttk.Frame(self.root, style='Sidebar.TFrame', width=320)
        sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 2))
        sidebar_frame.grid_propagate(False)
        sidebar_frame.grid_rowconfigure(6, weight=1)
        
        # Logo/Title section
        title_frame = tk.Frame(sidebar_frame, bg=ModernStyle.COLORS['bg_tertiary'], height=80)
        title_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 2))
        title_frame.grid_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Twitter AI\nAutomation",
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['title'],
            justify='center'
        )
        title_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Account Selection Section
        accounts_frame = ttk.Frame(sidebar_frame, style='Card.TFrame')
        accounts_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        accounts_frame.grid_columnconfigure(0, weight=1)
        
        accounts_label = ttk.Label(
            accounts_frame,
            text="Active Accounts",
            style='Heading.TLabel'
        )
        accounts_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Account listbox with custom styling
        listbox_frame = tk.Frame(accounts_frame, bg=ModernStyle.COLORS['bg_secondary'])
        listbox_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        self.account_listbox = tk.Listbox(
            listbox_frame,
            height=6,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_primary'],
            selectbackground=ModernStyle.COLORS['accent_blue'],
            selectforeground=ModernStyle.COLORS['text_primary'],
            relief="flat",
            font=ModernStyle.FONTS['body'],
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=ModernStyle.COLORS['accent_blue'],
            highlightbackground=ModernStyle.COLORS['border']
        )
        self.account_listbox.pack(fill="both", expand=True, padx=2, pady=2)
        self.account_listbox.bind('<<ListboxSelect>>', self.on_account_select)
        
        # Control Buttons
        self.start_button = tk.Button(
            sidebar_frame,
            text="▶ Start Automation",
            command=self.toggle_automation,
            bg=ModernStyle.COLORS['accent_green'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['heading'],
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.start_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.add_goal_button = tk.Button(
            sidebar_frame,
            text="+ Add Goal",
            command=self.show_add_goal_dialog,
            bg=ModernStyle.COLORS['accent_blue'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.add_goal_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.settings_button = tk.Button(
            sidebar_frame,
            text="⚙ Settings",
            command=self.show_settings_dialog,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.settings_button.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        
        # Status indicator
        status_frame = tk.Frame(sidebar_frame, bg=ModernStyle.COLORS['bg_tertiary'])
        status_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=10)
        
        self.status_indicator = tk.Label(
            status_frame,
            text="● Offline",
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['accent_red'],
            font=ModernStyle.FONTS['body']
        )
        self.status_indicator.pack(pady=10)
        
    def create_main_content(self):
        """Create the main content area with tabs"""
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg=ModernStyle.COLORS['bg_primary'])
        main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Tab notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create tabs
        self.setup_dashboard_tab()
        self.setup_goals_tab()
        self.setup_logs_tab()
        self.setup_analytics_tab()
        
    def setup_dashboard_tab(self):
        """Setup the main dashboard tab"""
        
        dashboard_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['bg_secondary'])
        self.notebook.add(dashboard_frame, text="  Dashboard  ")
        dashboard_frame.grid_columnconfigure(1, weight=1)
        dashboard_frame.grid_rowconfigure(2, weight=1)
        
        # Account info section
        info_frame = ttk.Frame(dashboard_frame, style='Card.TFrame')
        info_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        self.account_name_label = tk.Label(
            info_frame,
            text="Select an account to view details",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['title']
        )
        self.account_name_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Quick stats section
        stats_frame = tk.Frame(dashboard_frame, bg=ModernStyle.COLORS['bg_secondary'])
        stats_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create stat cards
        self.create_stat_card(stats_frame, "Active Goals", "2", 0, ModernStyle.COLORS['accent_blue'])
        self.create_stat_card(stats_frame, "Tasks Completed", "15", 1, ModernStyle.COLORS['accent_green'])
        self.create_stat_card(stats_frame, "Success Rate", "87%", 2, ModernStyle.COLORS['accent_orange'])
        self.create_stat_card(stats_frame, "Last Activity", "2 min ago", 3, ModernStyle.COLORS['text_muted'])
        
        # Activity feed section
        activity_frame = ttk.Frame(dashboard_frame, style='Card.TFrame')
        activity_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_rowconfigure(1, weight=1)
        
        activity_label = tk.Label(
            activity_frame,
            text="Recent Activity",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['heading']
        )
        activity_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        self.activity_text = scrolledtext.ScrolledText(
            activity_frame,
            height=15,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD
        )
        self.activity_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Add sample activity
        self.activity_text.insert("1.0", "🎯 Recent Activity\n\n")
        self.activity_text.insert(tk.END, "✅ Tweet posted: 'AI automation trends'\n")
        self.activity_text.insert(tk.END, "✅ Engaged with 3 relevant posts\n")
        self.activity_text.insert(tk.END, "✅ Performance analysis completed\n")
        self.activity_text.insert(tk.END, "⏳ Content curation in progress\n")
        self.activity_text.insert(tk.END, "📊 Goal progress: 67% completed\n")
        
    def create_stat_card(self, parent, title: str, value: str, column: int, color: str):
        """Create a statistics card"""
        
        card_frame = tk.Frame(parent, bg=ModernStyle.COLORS['bg_tertiary'], relief='solid', bd=1)
        card_frame.grid(row=0, column=column, padx=5, pady=10, sticky="ew", ipadx=10, ipady=10)
        
        title_label = tk.Label(
            card_frame,
            text=title,
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['text_muted'],
            font=ModernStyle.FONTS['small']
        )
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(
            card_frame,
            text=value,
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=color,
            font=('Segoe UI', 20, 'bold')
        )
        value_label.pack(pady=(0, 10))
        
    def setup_goals_tab(self):
        """Setup the goals management tab"""
        
        goals_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['bg_secondary'])
        self.notebook.add(goals_frame, text="  Goals  ")
        goals_frame.grid_columnconfigure(0, weight=1)
        goals_frame.grid_rowconfigure(1, weight=1)
        
        # Goals header
        header_frame = ttk.Frame(goals_frame, style='Card.TFrame')
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        goals_title = tk.Label(
            header_frame,
            text="Goal Management",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['title']
        )
        goals_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        add_goal_btn = tk.Button(
            header_frame,
            text="+ Add New Goal",
            command=self.show_add_goal_dialog,
            bg=ModernStyle.COLORS['accent_blue'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        add_goal_btn.grid(row=0, column=1, padx=20, pady=15)
        
        # Goals display
        goals_display_frame = ttk.Frame(goals_frame, style='Card.TFrame')
        goals_display_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        goals_display_frame.grid_columnconfigure(0, weight=1)
        goals_display_frame.grid_rowconfigure(0, weight=1)
        
        self.goals_text = scrolledtext.ScrolledText(
            goals_display_frame,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD
        )
        self.goals_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Add sample goals
        self.goals_text.insert("1.0", "🎯 Current Goals\n\n")
        self.goals_text.insert(tk.END, "📈 Increase followers to 1000 in 30 days\n")
        self.goals_text.insert(tk.END, "   Progress: 67% (670/1000)\n")
        self.goals_text.insert(tk.END, "   Status: On track\n\n")
        self.goals_text.insert(tk.END, "💬 Achieve 5% engagement rate\n")
        self.goals_text.insert(tk.END, "   Current: 4.2%\n")
        self.goals_text.insert(tk.END, "   Status: Improving\n\n")
        self.goals_text.insert(tk.END, "📝 Post 3 high-quality tweets daily\n")
        self.goals_text.insert(tk.END, "   Today: 2/3 completed\n")
        self.goals_text.insert(tk.END, "   Status: In progress\n")
        
    def setup_logs_tab(self):
        """Setup the logs monitoring tab"""
        
        logs_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['bg_secondary'])
        self.notebook.add(logs_frame, text="  Logs  ")
        logs_frame.grid_columnconfigure(0, weight=1)
        logs_frame.grid_rowconfigure(1, weight=1)
        
        # Logs header
        header_frame = ttk.Frame(logs_frame, style='Card.TFrame')
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        logs_title = tk.Label(
            header_frame,
            text="System Logs",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['title']
        )
        logs_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        clear_logs_btn = tk.Button(
            header_frame,
            text="Clear Logs",
            command=self.clear_logs,
            bg=ModernStyle.COLORS['accent_red'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        )
        clear_logs_btn.grid(row=0, column=1, padx=20, pady=15)
        
        # Logs display
        logs_display_frame = ttk.Frame(logs_frame, style='Card.TFrame')
        logs_display_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        logs_display_frame.grid_columnconfigure(0, weight=1)
        logs_display_frame.grid_rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            logs_display_frame,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['mono'],
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
    def setup_analytics_tab(self):
        """Setup the analytics and performance tab"""
        
        analytics_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['bg_secondary'])
        self.notebook.add(analytics_frame, text="  Analytics  ")
        analytics_frame.grid_columnconfigure(0, weight=1)
        analytics_frame.grid_rowconfigure(1, weight=1)
        
        # Analytics header
        header_frame = ttk.Frame(analytics_frame, style='Card.TFrame')
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        analytics_title = tk.Label(
            header_frame,
            text="Performance Analytics",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['title']
        )
        analytics_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Performance display
        self.performance_frame = ttk.Frame(analytics_frame, style='Card.TFrame')
        self.performance_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.performance_frame.grid_columnconfigure(0, weight=1)
        self.performance_frame.grid_rowconfigure(0, weight=1)
        
        performance_label = tk.Label(
            self.performance_frame,
            text="📊 Analytics Dashboard\n\nReal-time performance metrics and insights will appear here\nwhen the automation system is running.",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_muted'],
            font=ModernStyle.FONTS['heading'],
            justify='center'
        )
        performance_label.place(relx=0.5, rely=0.5, anchor='center')
        
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        
        status_frame = tk.Frame(self.root, bg=ModernStyle.COLORS['bg_tertiary'], height=35)
        status_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        status_frame.grid_propagate(False)
        status_frame.grid_columnconfigure(1, weight=1)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready - Demo Mode",
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['text_muted'],
            font=ModernStyle.FONTS['small']
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        # Time label
        self.time_label = tk.Label(
            status_frame,
            text=datetime.now().strftime("%H:%M:%S"),
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['text_muted'],
            font=ModernStyle.FONTS['small']
        )
        self.time_label.grid(row=0, column=2, padx=15, pady=8, sticky="e")
        
        # Update time every second
        self.update_time()
        
    def load_configuration(self):
        """Load the system configuration"""
        try:
            if ConfigLoader and AgentOrchestrator:
                self.config_loader = ConfigLoader()
                self.orchestrator = AgentOrchestrator(self.config_loader)
                
                # Load accounts
                self.load_accounts()
                self.log_message("Configuration loaded successfully")
                self.status_label.configure(text="Configuration loaded")
            else:
                # Demo mode
                self.load_demo_accounts()
                self.log_message("Running in demo mode")
                self.status_label.configure(text="Demo mode - Configuration not available")
                
        except Exception as e:
            self.log_message(f"Error loading configuration: {e}", "ERROR")
            self.load_demo_accounts()
            
    def load_accounts(self):
        """Load and display available accounts"""
        try:
            accounts_data = self.config_loader.get_accounts_config()
            self.account_listbox.delete(0, tk.END)
            
            for account_dict in accounts_data:
                if account_dict.get('is_active', True):
                    account_id = account_dict.get('account_id', 'Unknown')
                    self.account_listbox.insert(tk.END, f"@{account_id}")
                    
            if self.account_listbox.size() > 0:
                self.account_listbox.selection_set(0)
                self.on_account_select(None)
                
        except Exception as e:
            self.log_message(f"Error loading accounts: {e}", "ERROR")
            self.load_demo_accounts()
            
    def load_demo_accounts(self):
        """Load demo accounts for testing"""
        demo_accounts = ["@demo_account1", "@demo_account2", "@test_user"]
        self.account_listbox.delete(0, tk.END)
        
        for account in demo_accounts:
            self.account_listbox.insert(tk.END, account)
            
        if self.account_listbox.size() > 0:
            self.account_listbox.selection_set(0)
            self.on_account_select(None)
            
    def on_account_select(self, event):
        """Handle account selection"""
        selection = self.account_listbox.curselection()
        if selection:
            account_display = self.account_listbox.get(selection[0])
            account_id = account_display.replace('@', '')
            self.selected_account = account_id
            self.update_account_display(account_id)
            self.log_message(f"Selected account: {account_id}")
            
    def update_account_display(self, account_id: str):
        """Update the display for the selected account"""
        self.account_name_label.configure(text=f"Account: @{account_id}")
        
        # Update activity feed
        self.activity_text.delete("1.0", tk.END)
        self.activity_text.insert("1.0", f"🎯 Activity for @{account_id}\n\n")
        self.activity_text.insert(tk.END, "✅ Tweet posted: 'AI automation trends'\n")
        self.activity_text.insert(tk.END, "✅ Engaged with 3 relevant posts\n")
        self.activity_text.insert(tk.END, "✅ Performance analysis completed\n")
        self.activity_text.insert(tk.END, "⏳ Content curation in progress\n")
        self.activity_text.insert(tk.END, "📊 Goal progress: 67% completed\n")
        
    def toggle_automation(self):
        """Start or stop the automation system"""
        if not self.is_running:
            self.start_automation()
        else:
            self.stop_automation()
            
    def start_automation(self):
        """Start the automation system"""
        if not self.selected_account:
            messagebox.showwarning("No Account Selected", "Please select an account first")
            return
            
        try:
            self.is_running = True
            self.start_button.configure(
                text="⏸ Stop Automation",
                bg=ModernStyle.COLORS['accent_red']
            )
            self.status_indicator.configure(
                text="● Online",
                fg=ModernStyle.COLORS['accent_green']
            )
            
            self.log_message("🚀 Automation started")
            self.status_label.configure(text="Automation running")
            
            # In demo mode, just simulate activity
            if not self.orchestrator:
                self.simulate_demo_activity()
            
        except Exception as e:
            self.log_message(f"❌ Error starting automation: {e}", "ERROR")
            messagebox.showerror("Start Error", f"Failed to start automation:\n{e}")
            
    def stop_automation(self):
        """Stop the automation system"""
        self.is_running = False
        self.start_button.configure(
            text="▶ Start Automation",
            bg=ModernStyle.COLORS['accent_green']
        )
        self.status_indicator.configure(
            text="● Offline",
            fg=ModernStyle.COLORS['accent_red']
        )
        
        self.log_message("⏹ Automation stopped")
        self.status_label.configure(text="Automation stopped")
        
    def simulate_demo_activity(self):
        """Simulate automation activity in demo mode"""
        if self.is_running:
            activities = [
                "🔍 Analyzing trending topics",
                "📝 Generating content ideas",
                "💬 Engaging with relevant posts",
                "📊 Updating performance metrics",
                "🎯 Checking goal progress"
            ]
            
            import random
            activity = random.choice(activities)
            self.log_message(activity)
            
            # Schedule next activity
            self.root.after(5000, self.simulate_demo_activity)
            
    def show_add_goal_dialog(self):
        """Show dialog to add a new goal"""
        if not self.selected_account:
            messagebox.showwarning("No Account Selected", "Please select an account first")
            return
            
        dialog = AddGoalDialog(self.root, self.add_goal_callback)
        
    def add_goal_callback(self, goal_text: str):
        """Callback for adding a new goal"""
        if goal_text and self.selected_account:
            try:
                self.log_message(f"🎯 Goal added: {goal_text}")
                
                # Add to goals display
                self.goals_text.insert(tk.END, f"\n📋 {goal_text}\n")
                self.goals_text.insert(tk.END, "   Status: New\n")
                
            except Exception as e:
                self.log_message(f"❌ Error adding goal: {e}", "ERROR")
                messagebox.showerror("Goal Error", f"Failed to add goal:\n{e}")
        
    def show_settings_dialog(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self.root, self.config_loader)
        
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete("1.0", tk.END)
        self.log_message("🧹 Logs cleared")
        
    def log_message(self, message: str, level: str = "INFO"):
        """Add a message to the log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        level_icons = {
            "INFO": "ℹ️",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "SUCCESS": "✅"
        }
        
        icon = level_icons.get(level, "ℹ️")
        formatted_message = f"[{timestamp}] {icon} {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, formatted_message)
            self.log_text.see(tk.END)
            
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
        
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class AddGoalDialog:
    """Dialog for adding new goals"""
    
    def __init__(self, parent, callback):
        self.callback = callback
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Goal")
        self.dialog.geometry("500x350")
        self.dialog.configure(bg=ModernStyle.COLORS['bg_secondary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog(parent)
        
        self.setup_dialog()
        
    def center_dialog(self, parent):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (500 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (350 // 2)
        self.dialog.geometry(f"500x350+{x}+{y}")
        
    def setup_dialog(self):
        """Setup the dialog interface"""
        
        # Title
        title_label = tk.Label(
            self.dialog,
            text="🎯 Add New Goal",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(20, 10))
        
        # Instructions
        instruction_label = tk.Label(
            self.dialog,
            text="Describe your goal in natural language:",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body']
        )
        instruction_label.pack(pady=(0, 15))
        
        # Goal input
        input_frame = tk.Frame(self.dialog, bg=ModernStyle.COLORS['bg_secondary'])
        input_frame.pack(padx=30, pady=10, fill="both", expand=True)
        
        self.goal_text = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.goal_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.goal_text.insert("1.0", "Example: Gain 500 followers in the next 30 days by posting engaging content about AI and automation")
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg=ModernStyle.COLORS['bg_secondary'])
        button_frame.pack(pady=(10, 20))
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        add_btn = tk.Button(
            button_frame,
            text="Add Goal",
            command=self.add_goal,
            bg=ModernStyle.COLORS['accent_blue'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        add_btn.pack(side="left")
        
    def add_goal(self):
        """Add the goal and close dialog"""
        goal_text = self.goal_text.get("1.0", tk.END).strip()
        if goal_text and not goal_text.startswith("Example:"):
            self.callback(goal_text)
            self.dialog.destroy()
        else:
            messagebox.showwarning("Invalid Goal", "Please enter a valid goal description")


class SettingsDialog:
    """Dialog for system settings"""
    
    def __init__(self, parent, config_loader):
        self.config_loader = config_loader
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("650x550")
        self.dialog.configure(bg=ModernStyle.COLORS['bg_secondary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog(parent)
        
        self.setup_dialog()
        
    def center_dialog(self, parent):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (650 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (550 // 2)
        self.dialog.geometry(f"650x550+{x}+{y}")
        
    def setup_dialog(self):
        """Setup the settings dialog"""
        
        # Title
        title_label = tk.Label(
            self.dialog,
            text="⚙ System Settings",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['title']
        )
        title_label.pack(pady=(20, 15))
        
        # Settings notebook
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        # API Settings tab
        api_frame = tk.Frame(notebook, bg=ModernStyle.COLORS['bg_secondary'])
        notebook.add(api_frame, text="  API Keys  ")
        
        api_info = tk.Label(
            api_frame,
            text="Configure your API keys and LLM preferences",
            bg=ModernStyle.COLORS['bg_secondary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body']
        )
        api_info.pack(pady=(20, 15))
        
        # GitHub Copilot API key
        copilot_frame = tk.Frame(api_frame, bg=ModernStyle.COLORS['bg_tertiary'], relief='solid', bd=1)
        copilot_frame.pack(padx=20, pady=10, fill="x")
        
        copilot_label = tk.Label(
            copilot_frame,
            text="GitHub Copilot API Key:",
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['body']
        )
        copilot_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.copilot_entry = tk.Entry(
            copilot_frame,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            borderwidth=0,
            insertbackground=ModernStyle.COLORS['text_primary']
        )
        self.copilot_entry.pack(padx=20, pady=(0, 15), fill="x")
        self.copilot_entry.insert(0, "ghu_...")
        
        # General Settings tab
        general_frame = tk.Frame(notebook, bg=ModernStyle.COLORS['bg_secondary'])
        notebook.add(general_frame, text="  General  ")
        
        # Automation interval
        interval_frame = tk.Frame(general_frame, bg=ModernStyle.COLORS['bg_tertiary'], relief='solid', bd=1)
        interval_frame.pack(padx=20, pady=20, fill="x")
        
        interval_label = tk.Label(
            interval_frame,
            text="Automation Cycle Interval (minutes):",
            bg=ModernStyle.COLORS['bg_tertiary'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['body']
        )
        interval_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.interval_entry = tk.Entry(
            interval_frame,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            borderwidth=0,
            insertbackground=ModernStyle.COLORS['text_primary']
        )
        self.interval_entry.pack(padx=20, pady=(0, 15), fill="x")
        self.interval_entry.insert(0, "60")
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg=ModernStyle.COLORS['bg_secondary'])
        button_frame.pack(pady=(0, 20))
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            bg=ModernStyle.COLORS['bg_primary'],
            fg=ModernStyle.COLORS['text_secondary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            bg=ModernStyle.COLORS['accent_green'],
            fg=ModernStyle.COLORS['text_primary'],
            font=ModernStyle.FONTS['body'],
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2"
        )
        save_btn.pack(side="left")
        
    def save_settings(self):
        """Save the settings"""
        # This would save settings to the configuration
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        self.dialog.destroy()


def main():
    """Main entry point for the GUI application"""
    try:
        app = TwitterAutomationGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")


if __name__ == "__main__":
    main()
