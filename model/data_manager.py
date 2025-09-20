import json
import os
from datetime import datetime
from typing import List, Any
from model.entities import User, ProjectData, RewardTier, StretchGoal, Pledge

class DataManager:
    """Handles loading and saving of all data from/to JSON files."""
    def __init__(self, data_folder: str):
        self.data_folder = data_folder
        self.users: List[User] = self._load_data('users.json', User)
        self.projects_data: List[ProjectData] = self._load_data('projects.json', ProjectData)
        self.pledges: List[Pledge] = self._load_data('pledges.json', Pledge)
        self._link_related_data()

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.data_folder, filename)

    def _load_data(self, filename: str, cls) -> List[Any]:
        """
        Loads data from a JSON file, instantiates the given class,
        and then robustly corrects the types for datetime fields.
        """
        path = self._get_path(filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            instances = [cls(**item) for item in data]

            for instance in instances:
                if hasattr(instance, 'deadline') and isinstance(getattr(instance, 'deadline'), str):
                    setattr(instance, 'deadline', datetime.fromisoformat(getattr(instance, 'deadline')))
                if hasattr(instance, 'timestamp') and isinstance(getattr(instance, 'timestamp'), str):
                    setattr(instance, 'timestamp', datetime.fromisoformat(getattr(instance, 'timestamp')))
            
            return instances
            
        except FileNotFoundError:
            print(f"WARNING: Data file not found at '{path}'. Returning empty list.")
            return []
        except json.JSONDecodeError:
            print(f"WARNING: Could not parse JSON from '{path}'. Returning empty list.")
            return []

    def _link_related_data(self):
        """Links reward tiers and stretch goals to their respective projects."""
        reward_tiers = self._load_data('reward_tiers.json', RewardTier)
        stretch_goals = self._load_data('stretch_goals.json', StretchGoal)

        for proj_data in self.projects_data:
            proj_data.reward_tiers = [rt for rt in reward_tiers if rt.project_id == proj_data.project_id]
            proj_data.stretch_goals = [sg for sg in stretch_goals if sg.project_id == proj_data.project_id]

    def save_pledges(self):
        """Saves the current list of pledges to its JSON file."""
        with open(self._get_path('pledges.json'), 'w', encoding='utf-8') as f:
            pledges_dict = [
                {**p.__dict__, 'timestamp': p.timestamp.isoformat()} 
                for p in self.pledges
            ]
            json.dump(pledges_dict, f, indent=4)
            
    def get_pledges_for_project(self, project_id: str) -> List[Pledge]:
        return [p for p in self.pledges if p.project_id == project_id]

    def add_pledge(self, pledge: Pledge):
        self.pledges.append(pledge)
        self.save_pledges()

    def find_user_by_username(self, username: str) -> User | None:
        return next((u for u in self.users if u.username.lower() == username.lower()), None)