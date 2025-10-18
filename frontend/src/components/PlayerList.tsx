import React from 'react';
import { Player } from '../types/game.types';

interface PlayerListProps {
  players: Player[];
  czarId?: string | null;
  currentPlayerId?: string | null;
}

export const PlayerList: React.FC<PlayerListProps> = ({
  players,
  czarId,
  currentPlayerId,
}) => {
  return (
    <div className="bg-game-card rounded-xl p-4 shadow-lg">
      <h3 className="text-xl font-bold text-white mb-4">Players</h3>
      <div className="space-y-2">
        {players.map((player) => (
          <div
            key={player.id}
            className={`
              p-3 rounded-lg flex items-center justify-between
              transition-all duration-300
              ${player.id === currentPlayerId ? 'bg-game-accent' : 'bg-game-bg'}
              ${!player.is_connected ? 'opacity-50' : ''}
            `}
          >
            <div className="flex items-center space-x-3">
              <div
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center
                  font-bold text-lg
                  ${(player.type === 'ai' || player.type.includes('AI')) ? 'bg-purple-600' : 'bg-blue-600'}
                `}
              >
                {player.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-white font-semibold">{player.name}</span>
                  {(player.type === 'ai' || player.type.includes('AI')) && (
                    <span className="bg-purple-500 text-white text-xs px-2 py-1 rounded-full">
                      AI
                    </span>
                  )}
                  {player.id === czarId && (
                    <span className="bg-yellow-500 text-black text-xs px-2 py-1 rounded-full font-bold">
                      👑 CZAR
                    </span>
                  )}
                </div>
                {!player.is_connected && (
                  <span className="text-xs text-gray-400">Disconnected</span>
                )}
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-game-highlight">
                {player.score}
              </div>
              <div className="text-xs text-gray-400">points</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
