from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import uuid


class PlayerType(str, Enum):
    HUMAN = "human"
    AI = "ai"


class AIPersonality(str, Enum):
    ABSURD = "absurd"
    EDGY = "edgy"
    WHOLESOME = "wholesome"
    CHAOTIC = "chaotic"
    SARCASTIC = "sarcastic"
    PUNNY = "punny"
    DARK_HUMOR = "dark_humor"
    INNOCENT = "innocent"


class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=50)
    type: PlayerType = PlayerType.HUMAN
    score: int = Field(default=0)
    hand: List[str] = Field(default_factory=list, description="Card IDs in hand")
    is_connected: bool = Field(default=True)
    socket_id: Optional[str] = Field(default=None)
    
    class Config:
        use_enum_values = True


class AIPlayer(Player):
    """AI-controlled player"""
    type: PlayerType = PlayerType.AI
    personality: AIPersonality = AIPersonality.ABSURD
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    class Config:
        use_enum_values = True
