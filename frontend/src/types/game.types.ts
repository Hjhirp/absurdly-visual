export type CardType = 'black' | 'white';
export type PlayerType = 'human' | 'ai';
export type GameState = 'lobby' | 'playing' | 'judging' | 'round_end' | 'game_end';

export interface Card {
  id: string;
  text: string;
  type: CardType;
  pack: string;
}

export interface BlackCard extends Card {
  type: 'black';
  pick: number;
}

export interface WhiteCard extends Card {
  type: 'white';
  nsfw: boolean;
}

export interface Player {
  id: string;
  name: string;
  type: PlayerType;
  score: number;
  is_connected: boolean;
  card_count?: number;
}

export interface Submission {
  player_id: string | null;
  cards: WhiteCard[];
  video_url?: string;
  image_url?: string;
  audio_url?: string;
}

export interface Round {
  round_number: number;
  black_card: BlackCard;
  czar_id: string;
  submissions_count: number;
  submissions: Submission[];
  winner_id: string | null;
  video_url: string | null;
}

export interface GameStateData {
  game_id: string;
  state: GameState;
  players: Player[];
  your_hand: WhiteCard[];
  current_round: Round | null;
  points_to_win: number;
}

export interface SocketEvents {
  // Client -> Server
  create_game: (data: { player_name: string; settings?: any }) => void;
  join_game: (data: { game_id: string; player_name: string; is_ai?: boolean }) => void;
  start_game: (data: { game_id: string }) => void;
  submit_cards: (data: { game_id: string; player_id: string; card_ids: string[] }) => void;
  select_winner: (data: { game_id: string; player_id: string; winning_submission: number }) => void;
  request_ai_join: (data: { game_id: string; personality?: string }) => void;
  send_message: (data: { game_id: string; player_id: string; message: string; timestamp: string }) => void;

  // Server -> Client
  connected: (data: { sid: string }) => void;
  game_created: (data: { game_id: string; player_id: string; game_state: GameStateData }) => void;
  game_state: (data: GameStateData) => void;
  player_joined: (data: { player: Player }) => void;
  player_left: (data: { player_id: string; player_name: string }) => void;
  round_started: (data: { round_number: number }) => void;
  cards_submitted: (data: { player_id: string; player_name: string; count: number }) => void;
  judging_phase: () => void;
  winner_selected: (data: {
    winner_id: string;
    winner_name: string;
    black_card: BlackCard;
    white_cards: WhiteCard[];
    video_url: string | null;
  }) => void;
  video_ready: (data: { video_url: string }) => void;
  chat_message: (data: { player_id: string; player_name: string; message: string; timestamp: string }) => void;
  error: (data: { message: string }) => void;
}
