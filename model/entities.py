from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class User:
    user_id: str
    username: str

@dataclass
class RewardTier:
    project_id: str
    name: str
    min_pledge: int
    quantity: Optional[int]

@dataclass
class StretchGoal:
    project_id: str
    unlock_amount: int
    description: str

@dataclass
class Pledge:
    user_id: str
    project_id: str
    amount: int
    timestamp: datetime
    reward_tier_name: Optional[str] = None

# เก็บ raw, static data ของ project จาก JSON file.
@dataclass
class ProjectData:
    project_id: str
    name: str
    goal: int
    deadline: datetime
    category: str
    has_stretch_goal: bool
    reward_tiers: List[RewardTier] = field(default_factory=list)
    stretch_goals: List[StretchGoal] = field(default_factory=list)