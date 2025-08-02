"""
Agentic Twitter Automation - Main Entry Point

This is the new main entry point for the AI-powered, autonomous Twitter automation system.
The system uses LLM agents to make intelligent decisions about content creation, curation,
engagement, and performance optimization.
"""

import asyncio
import argparse
import logging
import sys
import os
from datetime import datetime
from typing import Optional

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.core.config_loader import ConfigLoader
    from src.utils.logger import setup_logger
    from src.agents.orchestrator import AgentOrchestrator
except ImportError:
    # Fallback for different execution contexts
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.core.config_loader import ConfigLoader
    from src.utils.logger import setup_logger
    from src.agents.orchestrator import AgentOrchestrator


class AgenticTwitterAutomation:
    """Main application class for the agentic Twitter automation system"""
    
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.logger = setup_logger(self.config_loader)
        self.orchestrator: Optional[AgentOrchestrator] = None
        
    async def initialize(self):
        """Initialize the agentic system"""
        self.logger.info("=== Initializing Agentic Twitter Automation System ===")
        
        try:
            # Initialize the agent orchestrator
            self.orchestrator = AgentOrchestrator(self.config_loader)
            await self.orchestrator.initialize()
            
            self.logger.info("System initialization complete!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            return False
    
    async def add_goal_interactive(self):
        """Interactive goal addition"""
        print("\n=== Add New Goal ===")
        
        # Get available accounts
        if not self.orchestrator:
            print("System not initialized!")
            return
        
        accounts = list(self.orchestrator.core_agent.contexts.keys())
        if not accounts:
            print("No accounts available!")
            return
        
        # Select account
        print("Available accounts:")
        for i, account_id in enumerate(accounts):
            print(f"{i + 1}. {account_id}")
        
        try:
            choice = int(input("Select account (number): ")) - 1
            if choice < 0 or choice >= len(accounts):
                print("Invalid selection!")
                return
            
            selected_account = accounts[choice]
            
            # Get goal description
            goal_description = input("Enter your goal in natural language: ").strip()
            if not goal_description:
                print("Goal description cannot be empty!")
                return
            
            # Add the goal
            print(f"\nProcessing goal for {selected_account}...")
            goal = await self.orchestrator.add_goal_from_natural_language(
                account_id=selected_account,
                goal_description=goal_description
            )
            
            print(f"Goal added successfully!")
            print(f"Goal ID: {goal.id}")
            print(f"Description: {goal.description}")
            print(f"Target Metrics: {goal.target_metrics}")
            print(f"Deadline: {goal.deadline}")
            
        except ValueError:
            print("Invalid input! Please enter a number.")
        except Exception as e:
            print(f"Error adding goal: {e}")
    
    async def run_interactive_mode(self):
        """Run in interactive mode with menu options"""
        if not await self.initialize():
            return
        
        while True:
            print("\n" + "="*50)
            print("AGENTIC TWITTER AUTOMATION - INTERACTIVE MODE")
            print("="*50)
            print("1. Add new goal")
            print("2. Run single cycle (all accounts)")
            print("3. Run single cycle (specific account)")
            print("4. View system status")
            print("5. View account goals")
            print("6. View account tasks")
            print("7. Start continuous mode")
            print("8. Exit")
            print("-"*50)
            
            try:
                choice = input("Enter your choice (1-8): ").strip()
                
                if choice == "1":
                    await self.add_goal_interactive()
                
                elif choice == "2":
                    print("\nRunning execution cycle for all accounts...")
                    results = await self.orchestrator.run_single_cycle()
                    print("Cycle Results:")
                    for account_id, result in results.items():
                        print(f"  {account_id}: {result}")
                
                elif choice == "3":
                    accounts = list(self.orchestrator.core_agent.contexts.keys())
                    if not accounts:
                        print("No accounts available!")
                        continue
                    
                    print("Available accounts:")
                    for i, account_id in enumerate(accounts):
                        print(f"{i + 1}. {account_id}")
                    
                    try:
                        acc_choice = int(input("Select account (number): ")) - 1
                        if 0 <= acc_choice < len(accounts):
                            selected_account = accounts[acc_choice]
                            print(f"\nRunning cycle for {selected_account}...")
                            result = await self.orchestrator.run_single_cycle(selected_account)
                            print(f"Result: {result}")
                        else:
                            print("Invalid selection!")
                    except ValueError:
                        print("Invalid input!")
                
                elif choice == "4":
                    status = self.orchestrator.get_system_status()
                    print("\nSystem Status:")
                    print(f"Running: {status['is_running']}")
                    print(f"Active Accounts: {status['active_accounts']}")
                    print(f"Total Goals: {status['total_goals']}")
                    print(f"Pending Tasks: {status['pending_tasks']}")
                    
                    for account_id, acc_status in status['accounts'].items():
                        print(f"\n{account_id}:")
                        print(f"  Active Goals: {acc_status['active_goals']}")
                        print(f"  Pending Tasks: {acc_status['pending_tasks']}")
                        print(f"  Last Action: {acc_status['last_action']}")
                
                elif choice == "5":
                    accounts = list(self.orchestrator.core_agent.contexts.keys())
                    if not accounts:
                        print("No accounts available!")
                        continue
                    
                    print("Select account to view goals:")
                    for i, account_id in enumerate(accounts):
                        print(f"{i + 1}. {account_id}")
                    
                    try:
                        acc_choice = int(input("Enter number: ")) - 1
                        if 0 <= acc_choice < len(accounts):
                            selected_account = accounts[acc_choice]
                            goals = self.orchestrator.get_account_goals(selected_account)
                            
                            print(f"\nGoals for {selected_account}:")
                            for goal in goals:
                                print(f"  ID: {goal['id']}")
                                print(f"  Description: {goal['description']}")
                                print(f"  Progress: {goal['progress']:.1%}")
                                print(f"  Priority: {goal['priority']}")
                                print(f"  Active: {goal['is_active']}")
                                print("-" * 30)
                        else:
                            print("Invalid selection!")
                    except ValueError:
                        print("Invalid input!")
                
                elif choice == "6":
                    accounts = list(self.orchestrator.core_agent.contexts.keys())
                    if not accounts:
                        print("No accounts available!")
                        continue
                    
                    print("Select account to view tasks:")
                    for i, account_id in enumerate(accounts):
                        print(f"{i + 1}. {account_id}")
                    
                    try:
                        acc_choice = int(input("Enter number: ")) - 1
                        if 0 <= acc_choice < len(accounts):
                            selected_account = accounts[acc_choice]
                            tasks = self.orchestrator.get_account_tasks(selected_account)
                            
                            print(f"\nTasks for {selected_account}:")
                            for task in tasks:
                                print(f"  ID: {task['id']}")
                                print(f"  Role: {task['role']}")
                                print(f"  Description: {task['description']}")
                                print(f"  Status: {task['status']}")
                                print(f"  Priority: {task['priority']}")
                                print("-" * 30)
                        else:
                            print("Invalid selection!")
                    except ValueError:
                        print("Invalid input!")
                
                elif choice == "7":
                    print("Starting continuous mode...")
                    print("Press Ctrl+C to stop")
                    await self.orchestrator.run_continuous_mode()
                
                elif choice == "8":
                    print("Exiting...")
                    break
                
                else:
                    print("Invalid choice! Please enter 1-8.")
                    
            except KeyboardInterrupt:
                print("\nReceived interrupt signal...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        # Cleanup
        if self.orchestrator:
            await self.orchestrator.stop()
    
    async def run_continuous_mode(self):
        """Run in continuous mode"""
        if not await self.initialize():
            return
        
        self.logger.info("Starting continuous mode...")
        await self.orchestrator.run_continuous_mode()
    
    async def add_goal_cli(self, account_id: str, goal_description: str):
        """Add a goal via CLI"""
        if not await self.initialize():
            return
        
        try:
            goal = await self.orchestrator.add_goal_from_natural_language(
                account_id=account_id,
                goal_description=goal_description
            )
            
            print(f"Goal added successfully for {account_id}!")
            print(f"Goal ID: {goal.id}")
            print(f"Description: {goal.description}")
            print(f"Target Metrics: {goal.target_metrics}")
            
        except Exception as e:
            print(f"Error adding goal: {e}")
        finally:
            if self.orchestrator:
                await self.orchestrator.stop()
    
    async def run_single_cycle_cli(self, account_id: Optional[str] = None):
        """Run a single cycle via CLI"""
        if not await self.initialize():
            return
        
        try:
            results = await self.orchestrator.run_single_cycle(account_id)
            print("Execution Results:")
            for acc_id, result in results.items():
                print(f"{acc_id}: {result}")
                
        except Exception as e:
            print(f"Error running cycle: {e}")
        finally:
            if self.orchestrator:
                await self.orchestrator.stop()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agentic Twitter Automation System")
    parser.add_argument("--mode", choices=["interactive", "continuous", "single-cycle"], 
                       default="interactive", help="Run mode")
    parser.add_argument("--account", help="Account ID for single-cycle mode")
    parser.add_argument("--goal", help="Add a goal in natural language")
    parser.add_argument("--goal-account", help="Account ID for goal (required with --goal)")
    
    args = parser.parse_args()
    
    app = AgenticTwitterAutomation()
    
    try:
        if args.goal:
            if not args.goal_account:
                print("Error: --goal-account is required when using --goal")
                return
            await app.add_goal_cli(args.goal_account, args.goal)
        
        elif args.mode == "interactive":
            await app.run_interactive_mode()
        
        elif args.mode == "continuous":
            await app.run_continuous_mode()
        
        elif args.mode == "single-cycle":
            await app.run_single_cycle_cli(args.account)
    
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Application error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
