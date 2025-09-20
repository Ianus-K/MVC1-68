from datetime import datetime
from typing import List
from model.project_model import Project
from utils.helpers import create_progress_bar, clear_screen

class ConsoleView:
    def display_main_menu(self, username: str):
        print("\n==================================")
        print(f"  Crowdfunding Main Menu")
        print(f"  Logged in as: {username}")
        print("==================================")
        print("1. View All Projects")
        print("2. Logout")
        print("==================================")

    def get_menu_choice(self, prompt: str = "Enter your choice: ") -> str:
        return input(prompt).strip()

    def display_project_list(self, projects: List[Project]):
        clear_screen()
        print("==============================================")
        print("            All Crowdfunding Projects")
        print("         (Sorted by deadline approaching)")
        print("==============================================\n")
        if not projects:
            print("No projects found.")
            return

        for i, project in enumerate(projects, 1):
            days_left = (project.deadline - datetime.now()).days
            print(f"{i}. {project.name} [{project.data.category}]")
            print(f"   Goal: {project.goal:,} | Funded: {project.current_funding:,}")
            print(f"   Deadline: {project.deadline.strftime('%Y-%m-%d')} ({days_left} days left)")
            print(f"   {create_progress_bar(project.get_progress_percentage())}\n")
        
        print("----------------------------------------------")
        print("Enter a number to view details, or 'b' to go back.")

    def display_project_details(self, project: Project):
        clear_screen()
        days_left = (project.deadline - datetime.now()).days
        print("=====================================================")
        print(f"  Project: {project.name}")
        print("=====================================================")
        print(f"Category: {project.data.category}")
        print(f"Goal: {project.goal:,}")
        print(f"Currently Funded: {project.current_funding:,}")
        print(f"Deadline: {project.deadline.strftime('%Y-%m-%d')} ({days_left} days left)")
        print(f"Progress: {create_progress_bar(project.get_progress_percentage())}\n")

        print(project.get_status_details())

        if project.data.reward_tiers:
            print("--- Reward Tiers ---")
            for i, tier in enumerate(project.data.reward_tiers, 1):
                quantity_str = f"({tier.quantity} left)" if tier.quantity is not None else "(Unlimited)"
                print(f"{i}. {tier.name} - Min Pledge: {tier.min_pledge:,} {quantity_str}")
        
        print("\n-----------------------------------------------------")
        print("Enter 'p' to pledge, or 'b' to go back.")

    def get_login_credentials(self) -> str:
        clear_screen()
        print("===== Welcome to Crowdfunding System =====")
        return input("Enter your username to login: ").strip()
    
    def get_pledge_info(self, project: Project) -> tuple[str, str]:
        reward_choice = "" # ค่าเริ่มต้น ยังไม่เลือกรางวัล

        # เช็คว่าโปรเจกต์มี Reward Tiers ไหม
        if project.data.reward_tiers:
            reward_choice = input(f"Enter reward tier number to select (1-{len(project.data.reward_tiers)}), or press Enter to skip: ").strip()
        
        amount_str = input("Enter amount to pledge: ").strip()
        return reward_choice, amount_str

    def show_message(self, message: str, error: bool = False):
        prefix = "ERROR:" if error else "INFO:"
        print(f"\n>> {prefix} {message}")
        input("   Press Enter to continue...")