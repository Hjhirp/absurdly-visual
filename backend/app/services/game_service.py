from typing import Dict, List, Optional
from datetime import datetime
from ..models.game import Game, GameState, Round, Submission
from ..models.player import Player, AIPlayer, PlayerType
from .card_service import card_service
import random


class GameService:
    """Service for managing game state and logic"""
    
    def __init__(self):
        self.games: Dict[str, Game] = {}
        self.players: Dict[str, Player] = {}
    
    def create_game(self, creator_id: str, settings: dict = None) -> Game:
        """Create a new game"""
        game = Game(**(settings or {}))
        game.players.append(creator_id)
        
        # Initialize decks
        game.black_deck = card_service.create_shuffled_deck("black")
        game.white_deck = card_service.create_shuffled_deck("white", game.censorship_level)
        
        self.games[game.id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[Game]:
        """Get a game by ID"""
        return self.games.get(game_id)
    
    def add_player(self, game_id: str, player: Player) -> bool:
        """Add a player to a game"""
        game = self.get_game(game_id)
        if not game or len(game.players) >= game.max_players:
            return False
        
        if player.id not in game.players:
            game.players.append(player.id)
            self.players[player.id] = player
            game.updated_at = datetime.utcnow()
        
        return True
    
    def remove_player(self, game_id: str, player_id: str) -> bool:
        """Remove a player from a game"""
        game = self.get_game(game_id)
        if not game or player_id not in game.players:
            return False
        
        game.players.remove(player_id)
        
        # Mark player as disconnected instead of deleting
        if player_id in self.players:
            self.players[player_id].is_connected = False
        
        game.updated_at = datetime.utcnow()
        
        # If game is in progress and too few players, pause or end
        if game.state == GameState.PLAYING and len(game.players) < game.min_players:
            game.state = GameState.LOBBY
        
        return True
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID"""
        return self.players.get(player_id)
    
    def start_game(self, game_id: str) -> bool:
        """Start a game"""
        game = self.get_game(game_id)
        if not game or len(game.players) < game.min_players:
            return False
        
        if game.state != GameState.LOBBY:
            return False
        
        # Deal initial hands
        for player_id in game.players:
            self._deal_cards(game, player_id, game.cards_per_hand)
        
        # Start first round
        self.start_round(game_id)
        
        return True
    
    def start_round(self, game_id: str) -> bool:
        """Start a new round"""
        game = self.get_game(game_id)
        if not game:
            return False
        
        # Draw black card
        if not game.black_deck:
            # Reshuffle discard pile
            game.black_deck = game.black_discard.copy()
            random.shuffle(game.black_deck)
            game.black_discard.clear()
        
        if not game.black_deck:
            return False
        
        black_card_id = game.black_deck.pop()
        czar_id = game.get_current_czar()
        
        round_number = len(game.round_history) + 1
        game.current_round = Round(
            round_number=round_number,
            black_card_id=black_card_id,
            czar_id=czar_id
        )
        
        game.state = GameState.PLAYING
        game.updated_at = datetime.utcnow()
        
        return True
    
    def submit_cards(self, game_id: str, player_id: str, card_ids: List[str]) -> bool:
        """Submit white cards for the current round"""
        game = self.get_game(game_id)
        player = self.get_player(player_id)
        
        if not game or not player or not game.current_round:
            return False
        
        # Can't submit if you're the czar
        if player_id == game.current_round.czar_id:
            return False
        
        # Check if already submitted
        if any(sub.player_id == player_id for sub in game.current_round.submissions):
            return False
        
        # Validate cards are in player's hand
        if not all(card_id in player.hand for card_id in card_ids):
            return False
        
        # Create submission
        submission = Submission(player_id=player_id, card_ids=card_ids)
        game.current_round.submissions.append(submission)
        
        # Remove cards from hand
        for card_id in card_ids:
            player.hand.remove(card_id)
            game.white_discard.append(card_id)
        
        # Check if all players have submitted
        non_czar_players = [p for p in game.players if p != game.current_round.czar_id]
        if len(game.current_round.submissions) == len(non_czar_players):
            game.state = GameState.JUDGING
        
        game.updated_at = datetime.utcnow()
        return True
    
    def select_winner(self, game_id: str, czar_id: str, winning_submission_index: int) -> bool:
        """Czar selects the winning submission"""
        game = self.get_game(game_id)
        
        if not game or not game.current_round:
            return False
        
        if czar_id != game.current_round.czar_id:
            return False
        
        if game.state != GameState.JUDGING:
            return False
        
        if winning_submission_index >= len(game.current_round.submissions):
            return False
        
        # Set winner
        winning_submission = game.current_round.submissions[winning_submission_index]
        game.current_round.winner_id = winning_submission.player_id
        game.current_round.ended_at = datetime.utcnow()
        
        # Update player score
        winner = self.get_player(winning_submission.player_id)
        if winner:
            winner.score += 1
        
        # Check for game winner
        if winner and winner.score >= game.points_to_win:
            game.state = GameState.GAME_END
        else:
            game.state = GameState.ROUND_END
        
        game.updated_at = datetime.utcnow()
        return True
    
    def end_round(self, game_id: str) -> bool:
        """End the current round and prepare for next"""
        game = self.get_game(game_id)
        
        if not game or not game.current_round:
            return False
        
        # Move current round to history
        game.round_history.append(game.current_round)
        game.black_discard.append(game.current_round.black_card_id)
        
        # Deal cards to players who played
        for submission in game.current_round.submissions:
            cards_played = len(submission.card_ids)
            self._deal_cards(game, submission.player_id, cards_played)
        
        # Rotate czar
        game.next_czar()
        
        # Clear current round
        game.current_round = None
        
        # Start next round
        if game.state != GameState.GAME_END:
            self.start_round(game_id)
        
        return True
    
    def _deal_cards(self, game: Game, player_id: str, count: int):
        """Deal cards to a player"""
        player = self.get_player(player_id)
        if not player:
            return
        
        for _ in range(count):
            if not game.white_deck:
                # Reshuffle discard pile
                game.white_deck = game.white_discard.copy()
                random.shuffle(game.white_deck)
                game.white_discard.clear()
            
            if game.white_deck:
                card_id = game.white_deck.pop()
                player.hand.append(card_id)
    
    def add_ai_player(self, game_id: str, personality: str = "absurd") -> Optional[AIPlayer]:
        """Add an AI player to the game"""
        game = self.get_game(game_id)
        if not game or len(game.players) >= game.max_players:
            return None
        
        ai_player = AIPlayer(
            name=f"AI Bot {len([p for p in self.players.values() if p.type == PlayerType.AI]) + 1}",
            personality=personality
        )
        
        if self.add_player(game_id, ai_player):
            return ai_player
        
        return None
    
    def get_game_state_for_player(self, game_id: str, player_id: str) -> dict:
        """Get game state from a player's perspective"""
        import json
        
        game = self.get_game(game_id)
        player = self.get_player(player_id)
        
        if not game or not player:
            return {}
        
        # Build player list with scores - ensure all values are JSON serializable
        players_data = []
        for pid in game.players:
            p = self.get_player(pid)
            if p:
                players_data.append({
                    "id": str(p.id),
                    "name": str(p.name),
                    "type": str(p.type),
                    "score": int(p.score),
                    "is_connected": bool(p.is_connected),
                    "card_count": int(len(p.hand))
                })
        
        # Build current round data
        round_data = None
        if game.current_round:
            black_card = card_service.get_black_card(game.current_round.black_card_id)
            round_data = {
                "round_number": int(game.current_round.round_number),
                "black_card": {
                    "id": str(black_card.id),
                    "text": str(black_card.text),
                    "type": str(black_card.type),
                    "pick": int(black_card.pick),
                    "pack": str(black_card.pack)
                } if black_card else None,
                "czar_id": str(game.current_round.czar_id) if game.current_round.czar_id else None,
                "submissions_count": int(len(game.current_round.submissions)),
                "submissions": [
                    {
                        "player_id": str(sub.player_id) if (game.state == GameState.ROUND_END and sub.player_id) else None,
                        "cards": [
                            {
                                "id": str(card.id),
                                "text": str(card.text),
                                "type": str(card.type),
                                "nsfw": bool(card.nsfw),
                                "pack": str(card.pack)
                            } for cid in sub.card_ids if (card := card_service.get_white_card(cid))
                        ]
                    }
                    for sub in game.current_round.submissions
                ] if game.state == GameState.JUDGING or game.state == GameState.ROUND_END else [],
                "winner_id": str(game.current_round.winner_id) if game.current_round.winner_id else None,
                "video_url": str(game.current_round.video_url) if game.current_round.video_url else None
            }
        
        result = {
            "game_id": str(game.id),
            "state": str(game.state),
            "players": players_data,
            "your_hand": [
                {
                    "id": str(card.id),
                    "text": str(card.text),
                    "type": str(card.type),
                    "nsfw": bool(card.nsfw),
                    "pack": str(card.pack)
                } for cid in player.hand if (card := card_service.get_white_card(cid))
            ],
            "current_round": round_data,
            "points_to_win": int(game.points_to_win)
        }
        
        # Verify it's JSON serializable
        try:
            json.dumps(result)
        except Exception as e:
            print(f"❌ Game state not JSON serializable: {e}")
            return {}
        
        return result


# Singleton instance
game_service = GameService()
