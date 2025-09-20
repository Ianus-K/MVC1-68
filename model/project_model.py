from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple
from model.entities import ProjectData, Pledge, RewardTier, StretchGoal

class Project(ABC):
    """Abstract Base Class for all project types."""
    def __init__(self, data: ProjectData, pledges: List[Pledge]):
        self.data = data
        self._pledges = pledges
        self.current_funding = sum(p.amount for p in self._pledges)

    @property
    def id(self) -> str:
        return self.data.project_id

    @property
    def name(self) -> str:
        return self.data.name
        
    @property
    def deadline(self) -> datetime:
        return self.data.deadline

    @property
    def goal(self) -> int:
        return self.data.goal

    def get_progress_percentage(self) -> float:
        if self.goal == 0:
            return 100.0
        return (self.current_funding / self.goal) * 100

    def is_funded(self) -> bool:
        return self.current_funding >= self.goal

    def add_pledge(self, pledge: Pledge, reward_tier: RewardTier | None) -> Tuple[bool, str]:
        """Validates and adds a new pledge. Returns (success, message)."""
        # Deadline must be in the future
        if datetime.now() > self.data.deadline:
            return False, "Project deadline has passed."
        
        # Pledge amount must be >= reward tier minimum
        if reward_tier and pledge.amount < reward_tier.min_pledge:
            return False, f"Pledge amount must be at least {reward_tier.min_pledge} for '{reward_tier.name}'."
        
        # Check reward quantity
        if reward_tier and reward_tier.quantity is not None:
            if reward_tier.quantity <= 0:
                return False, f"Reward '{reward_tier.name}' is out of stock."
            reward_tier.quantity -= 1
        
        self._pledges.append(pledge)
        self.current_funding += pledge.amount
        return True, "Pledge successful!"
    
    @abstractmethod
    def get_status_details(self) -> str:
        """Returns a string with status details specific to the project type."""
        pass


class SimpleProject(Project):
    """Model for a project without stretch goals."""
    def get_status_details(self) -> str:
        status = "Funded!" if self.is_funded() else "Funding in progress."
        return f"Status: {status}\n"


class StretchGoalProject(SimpleProject):
    """Model for a project with stretch goals."""
    def get_unlocked_stretch_goals(self) -> List[StretchGoal]:
        unlocked = [
            sg for sg in sorted(self.data.stretch_goals, key=lambda x: x.unlock_amount) 
            if self.current_funding >= sg.unlock_amount
        ]
        return unlocked

    def get_next_stretch_goal(self) -> StretchGoal | None:
        next_goals = [
            sg for sg in sorted(self.data.stretch_goals, key=lambda x: x.unlock_amount)
            if self.current_funding < sg.unlock_amount
        ]
        return next_goals[0] if next_goals else None

    def get_status_details(self) -> str:
        base_status = super().get_status_details()
        stretch_goal_info = "\n--- Stretch Goals ---\n"
        
        unlocked = self.get_unlocked_stretch_goals()
        if unlocked:
            for goal in unlocked:
                stretch_goal_info += f"[UNLOCKED] At {goal.unlock_amount:,}: {goal.description}\n"
        else:
            stretch_goal_info += "No stretch goals unlocked yet.\n"
            
        next_goal = self.get_next_stretch_goal()
        if next_goal:
            needed = next_goal.unlock_amount - self.current_funding
            stretch_goal_info += f"Next Goal: {next_goal.description} (Needs {needed:,} more)\n"
        
        return base_status + stretch_goal_info