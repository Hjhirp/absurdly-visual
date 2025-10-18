import React, { useState } from 'react';

interface LobbyProps {
  onCreateGame: (playerName: string) => void;
  onJoinGame: (gameId: string, playerName: string) => void;
}

export const Lobby: React.FC<LobbyProps> = ({ onCreateGame, onJoinGame }) => {
  const [playerName, setPlayerName] = useState('');
  const [gameId, setGameId] = useState('');
  const [mode, setMode] = useState<'menu' | 'create' | 'join'>('menu');

  const handleCreateGame = () => {
    if (playerName.trim()) {
      onCreateGame(playerName.trim());
    }
  };

  const handleJoinGame = () => {
    if (playerName.trim() && gameId.trim()) {
      onJoinGame(gameId.trim(), playerName.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-game-bg via-game-accent to-game-bg flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-6xl font-bold text-white mb-4">
            🎭 Absurdly Visual
          </h1>
          <p className="text-xl text-gray-300">
            Cards Against Humanity meets AI Video Generation
          </p>
          <p className="text-sm text-gray-400 mt-2">
            Powered by Fetch.ai, Veo3, and Gemini
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-game-card rounded-2xl shadow-2xl p-8 animate-slide-in">
          {mode === 'menu' && (
            <div className="space-y-4">
              <button
                onClick={() => setMode('create')}
                className="w-full bg-game-highlight hover:bg-red-600 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 text-lg"
              >
                🎮 Create New Game
              </button>
              <button
                onClick={() => setMode('join')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 text-lg"
              >
                🚪 Join Existing Game
              </button>

              <div className="mt-8 pt-8 border-t border-gray-700">
                <h3 className="text-white font-semibold mb-3">How to Play:</h3>
                <ul className="text-gray-300 space-y-2 text-sm">
                  <li>• Each round, one player is the Card Czar</li>
                  <li>• Others submit their funniest white cards</li>
                  <li>• Czar picks the winner</li>
                  <li>• AI generates a hilarious video of the winning combo! 🎬</li>
                  <li>• First to {7} points wins!</li>
                </ul>
              </div>
            </div>
          )}

          {mode === 'create' && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-white mb-4">Create Game</h2>
              <input
                type="text"
                placeholder="Enter your name"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleCreateGame()}
                className="w-full px-4 py-3 rounded-lg bg-game-bg text-white border-2 border-gray-700 focus:border-game-highlight focus:outline-none"
                maxLength={50}
              />
              <div className="flex space-x-3">
                <button
                  onClick={handleCreateGame}
                  disabled={!playerName.trim()}
                  className="flex-1 bg-game-highlight hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Game
                </button>
                <button
                  onClick={() => setMode('menu')}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all duration-300"
                >
                  Back
                </button>
              </div>
            </div>
          )}

          {mode === 'join' && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-white mb-4">Join Game</h2>
              <input
                type="text"
                placeholder="Enter your name"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-game-bg text-white border-2 border-gray-700 focus:border-game-highlight focus:outline-none"
                maxLength={50}
              />
              <input
                type="text"
                placeholder="Enter game ID"
                value={gameId}
                onChange={(e) => setGameId(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleJoinGame()}
                className="w-full px-4 py-3 rounded-lg bg-game-bg text-white border-2 border-gray-700 focus:border-game-highlight focus:outline-none"
              />
              <div className="flex space-x-3">
                <button
                  onClick={handleJoinGame}
                  disabled={!playerName.trim() || !gameId.trim()}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Join Game
                </button>
                <button
                  onClick={() => setMode('menu')}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all duration-300"
                >
                  Back
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-gray-400 text-sm">
          <p>Built for Fetch.ai Hackathon 2025</p>
        </div>
      </div>
    </div>
  );
};
