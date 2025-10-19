from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
import uuid


class GameState(str, Enum):
    LOBBY = "lobby"
    PLAYING = "playing"
    JUDGING = "judging"
    ROUND_END = "round_end"
    GAME_END = "game_end"


class Submission(BaseModel):
    player_id: str
    card_ids: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None


class Round(BaseModel):
    round_number: int
    black_card_id: str
    czar_id: str
    submissions: List[Submission] = Field(default_factory=list)
    winner_id: Optional[str] = None
    video_url: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class Game(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    state: GameState = GameState.LOBBY
    
    # Players
    players: List[str] = Field(default_factory=list, description="Player IDs")
    max_players: int = Field(default=8)
    min_players: int = Field(default=3)
    
    # Game settings
    points_to_win: int = Field(default=7)
    cards_per_hand: int = Field(default=5)
    censorship_level: str = Field(default="mild")  # none, mild, family
    topic: Optional[str] = Field(default=None, description="Game topic filter (Gaming, Tech, Sports, Art, Politics)")
    
    # Current round
    current_round: Optional[Round] = None
    round_history: List[Round] = Field(default_factory=list)
    
    # Card decks
    black_deck: List[str] = Field(default_factory=list, description="Remaining black card IDs")
    white_deck: List[str] = Field(default_factory=list, description="Remaining white card IDs")
    black_discard: List[str] = Field(default_factory=list)
    white_discard: List[str] = Field(default_factory=list)
    
    # Czar rotation
    czar_index: int = Field(default=0)
    
    class Config:
        use_enum_values = True
    
    def get_current_czar(self) -> Optional[str]:
        """Get the current card czar's player ID"""
        if not self.players:
            return None
        return self.players[self.czar_index % len(self.players)]
    
    def next_czar(self) -> str:
        """Rotate to the next czar"""
        self.czar_index = (self.czar_index + 1) % len(self.players)
        return self.get_current_czar()
    
    def get_scores(self) -> Dict[str, int]:
        """Calculate scores from round history"""
        scores = {player_id: 0 for player_id in self.players}
        for round_data in self.round_history:
            if round_data.winner_id:
                scores[round_data.winner_id] = scores.get(round_data.winner_id, 0) + 1
        return scores
    
    def check_winner(self) -> Optional[str]:
        """Check if any player has won the game"""
        scores = self.get_scores()
        for player_id, score in scores.items():
            if score >= self.points_to_win:
                return player_id
        return None
