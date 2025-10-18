import { useState, useEffect, useCallback } from 'react';
import { Socket } from 'socket.io-client';
import { GameStateData, Player } from '../types/game.types';

export const useGame = (socket: Socket | null) => {
  const [gameState, setGameState] = useState<GameStateData | null>(null);
  const [gameId, setGameId] = useState<string | null>(null);
  const [playerId, setPlayerId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    if (!socket) return;

    // Listen for game events
    socket.on('game_created', (data) => {
      setGameId(data.game_id);
      setPlayerId(data.player_id);
      setGameState(data.game_state);
      setNotification('Game created successfully!');
    });

    socket.on('game_joined', (data) => {
      setGameId(data.game_id);
      setPlayerId(data.player_id);
      setGameState(data.game_state);
      setNotification('Joined game successfully!');
    });

    socket.on('game_state', (data: GameStateData) => {
      setGameState(data);
    });

    socket.on('player_joined', (data: { player: Player }) => {
      setNotification(`${data.player.name} joined the game!`);
      
      // Update game state to include the new player
      setGameState((prevState) => {
        if (!prevState) return prevState;
        return {
          ...prevState,
          players: [...prevState.players, data.player]
        };
      });
    });

    socket.on('player_left', (data: { player_id: string; player_name: string }) => {
      setNotification(`${data.player_name} left the game`);
    });

    socket.on('round_started', (data: { round_number: number }) => {
      setNotification(`Round ${data.round_number} started!`);
    });

    socket.on('cards_submitted', (data) => {
      setNotification(`${data.player_name} submitted ${data.count} card(s)`);
    });

    socket.on('judging_phase', () => {
      setNotification('All cards submitted! Czar is judging...');
    });

    socket.on('winner_selected', (data) => {
      setNotification(`${data.winner_name} won this round!`);
    });

    socket.on('video_ready', (data) => {
      setNotification('Video is ready!');
    });

    socket.on('submission_videos_ready', (data: { videos: Record<number, string> }) => {
      console.log('📹 All submission videos ready:', data.videos);
      // Update game state with video URLs for each submission
      setGameState((prevState) => {
        if (!prevState || !prevState.current_round) return prevState;
        
        const updatedSubmissions = prevState.current_round.submissions.map((sub, idx) => ({
          ...sub,
          video_url: data.videos[idx] || ''
        }));
        
        return {
          ...prevState,
          current_round: {
            ...prevState.current_round,
            submissions: updatedSubmissions
          }
        };
      });
      setNotification('All videos are ready!');
    });

    socket.on('error', (data) => {
      setError(data.message);
    });

    return () => {
      socket.off('game_created');
      socket.off('game_joined');
      socket.off('game_state');
      socket.off('player_joined');
      socket.off('player_left');
      socket.off('round_started');
      socket.off('cards_submitted');
      socket.off('judging_phase');
      socket.off('winner_selected');
      socket.off('video_ready');
      socket.off('submission_videos_ready');
      socket.off('error');
    };
  }, [socket]);

  const createGame = useCallback((playerName: string, settings?: any) => {
    if (socket) {
      socket.emit('create_game', { player_name: playerName, settings });
    }
  }, [socket]);

  const joinGame = useCallback((gameId: string, playerName: string) => {
    if (socket) {
      socket.emit('join_game', { game_id: gameId, player_name: playerName });
      setGameId(gameId);
    }
  }, [socket]);

  const startGame = useCallback(() => {
    if (socket && gameId) {
      socket.emit('start_game', { game_id: gameId });
    }
  }, [socket, gameId]);

  const submitCards = useCallback((cardIds: string[]) => {
    if (socket && gameId && playerId) {
      socket.emit('submit_cards', {
        game_id: gameId,
        player_id: playerId,
        card_ids: cardIds,
      });
    }
  }, [socket, gameId, playerId]);

  const selectWinner = useCallback((submissionIndex: number) => {
    if (socket && gameId && playerId) {
      socket.emit('select_winner', {
        game_id: gameId,
        player_id: playerId,
        winning_submission: submissionIndex,
      });
    }
  }, [socket, gameId, playerId]);

  const requestAIJoin = useCallback((personality: string = 'absurd') => {
    console.log('🤖 Frontend: requestAIJoin called', { socket: !!socket, gameId });
    if (socket && gameId) {
      console.log('🤖 Frontend: Emitting request_ai_join', { game_id: gameId, personality });
      socket.emit('request_ai_join', { game_id: gameId, personality });
    } else {
      console.error('❌ Frontend: Cannot emit - socket or gameId missing', { socket: !!socket, gameId });
    }
  }, [socket, gameId]);

  const clearNotification = useCallback(() => {
    setNotification(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    gameState,
    gameId,
    playerId,
    error,
    notification,
    createGame,
    joinGame,
    startGame,
    submitCards,
    selectWinner,
    requestAIJoin,
    clearNotification,
    clearError,
  };
};
