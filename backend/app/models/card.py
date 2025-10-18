from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CardType(str, Enum):
    BLACK = "black"
    WHITE = "white"


class Card(BaseModel):
    id: str = Field(..., description="Unique card identifier")
    text: str = Field(..., description="Card text content")
    type: CardType = Field(..., description="Card type (black or white)")
    pack: str = Field(default="base", description="Card pack name")
    
    class Config:
        use_enum_values = True


class BlackCard(Card):
    """Question/prompt card"""
    type: CardType = CardType.BLACK
    pick: int = Field(default=1, description="Number of white cards to pick")
    
    def format_with_answers(self, answers: List[str]) -> str:
        """Format the black card with white card answers"""
        text = self.text
        for answer in answers:
            text = text.replace("_", answer, 1)
        return text


class WhiteCard(Card):
    """Answer card"""
    type: CardType = CardType.WHITE
    nsfw: bool = Field(default=False, description="Not safe for work flag")
    
    class Config:
        use_enum_values = True
