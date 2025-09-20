import sys
from datetime import datetime
from model.data_manager import DataManager
from model.project_model import Project, SimpleProject, StretchGoalProject
from model.entities import Pledge, User
from view.console_view import ConsoleView
from utils.helpers import clear_screen

class AppController:
    """Main controller for the application."""
    def __init__(self):
        self.view = ConsoleView()
        self.data_manager = DataManager(data_folder='data')
        self.projects: list[Project] = self._initialize_project_models()
        self.current_user: User | None = None
        self.rejected_pledges_count = 0

    def _initialize_project_models(self) -> list[Project]:
        """Factory method to create appropriate project model instances."""
        project_models = []
        for proj_data in self.data_manager.projects_data:
            pledges = self.data_manager.get_pledges_for_project(proj_data.project_id)
            if proj_data.has_stretch_goal:
                project_models.append(StretchGoalProject(proj_data, pledges))
            else:
                project_models.append(SimpleProject(proj_data, pledges))
        return project_models

    def run(self):
        """Main application loop."""
        while not self.current_user:
            self.handle_login()

        while self.current_user:
            clear_screen()
            self.view.display_main_menu(self.current_user.username)
            choice = self.view.get_menu_choice()
            if choice == '1':
                self.list_all_projects()
            elif choice == '2':
                self.handle_logout()
            else:
                self.view.show_message("Invalid choice. Please try again.", error=True)

    def handle_login(self):
        username = self.view.get_login_credentials()
        if not username:
            self.view.show_message("Username cannot be empty.", error=True)
            return
            
        user = self.data_manager.find_user_by_username(username)
        if user:
            self.current_user = user
            self.view.show_message(f"Welcome, {user.username}!")
        else:
            self.view.show_message("User not found.", error=True)

    def handle_logout(self):
        self.view.show_message(f"Goodbye, {self.current_user.username}!")
        self.current_user = None

    def list_all_projects(self):

        # Sort projects by deadline
        sorted_projects = sorted(self.projects, key=lambda p: p.deadline)
        
        while True:
            self.view.display_project_list(sorted_projects)
            choice = self.view.get_menu_choice()
            if choice.lower() == 'b':
                break
            try:
                project_index = int(choice) - 1
                if 0 <= project_index < len(sorted_projects):
                    self.view_project_details(sorted_projects[project_index])
                else:
                    self.view.show_message("Invalid project number.", error=True)
            except ValueError:
                self.view.show_message("Invalid input. Please enter a number or 'b'.", error=True)

    def view_project_details(self, project: Project):
        while True:
            self.view.display_project_details(project)
            choice = self.view.get_menu_choice()
            if choice.lower() == 'b':
                break
            elif choice.lower() == 'p':
                self.handle_pledge(project)
                
                # หลังบริจาคให้อยู่ดูข้อมูล update
            else:
                self.view.show_message("Invalid choice.", error=True)

    def handle_pledge(self, project: Project):
        reward_choice_str, amount_str = self.view.get_pledge_info(project)
        
        try:
            amount = int(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            self.rejected_pledges_count += 1
            self.view.show_message("Invalid pledge amount.", error=True)
            return

        selected_reward = None
        if reward_choice_str:
            try:
                reward_index = int(reward_choice_str) - 1
                if 0 <= reward_index < len(project.data.reward_tiers):
                    selected_reward = project.data.reward_tiers[reward_index]
                else:
                    raise ValueError("Invalid reward number.")
            except ValueError:
                self.rejected_pledges_count += 1
                self.view.show_message("Invalid reward tier selection.", error=True)
                return

        pledge = Pledge(
            user_id=self.current_user.user_id,
            project_id=project.id,
            amount=amount,
            timestamp=datetime.now(),
            reward_tier_name=selected_reward.name if selected_reward else None
        )

        success, message = project.add_pledge(pledge, selected_reward)

        if success:
            self.data_manager.add_pledge(pledge)
            self.view.show_message(message)
        else:
            self.rejected_pledges_count += 1
            self.view.show_message(message, error=True)
            print(f"Total rejected pledges in this session: {self.rejected_pledges_count}")