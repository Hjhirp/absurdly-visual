import React, { useEffect, useState } from 'react';
import { useSocket } from './hooks/useSocket';
import { useGame } from './hooks/useGame';
import { Lobby } from './components/Lobby';
import { GameRoom } from './components/GameRoom';
import { VideoFeed } from './components/VideoFeed';

function App() {
  const [showFeed, setShowFeed] = useState(false);
  const { socket, isConnected } = useSocket();
  const {
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
  } = useGame(socket);

  // Auto-clear notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        clearNotification();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [notification, clearNotification]);

  // Auto-clear errors
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  return (
    <div className="App font-game">
      {/* Connection Status */}
      {!isConnected && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-yellow-500 text-black px-6 py-3 rounded-lg shadow-lg z-50">
          Connecting to server...
        </div>
      )}

      {/* Notifications */}
      {notification && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in">
          {notification}
        </div>
      )}

      {/* Errors */}
      {error && (
        <div className="fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in">
          ❌ {error}
        </div>
      )}

      {/* Feed Toggle Button */}
      {!showFeed && (
        <button
          onClick={() => setShowFeed(true)}
          className="fixed bottom-4 right-4 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-full shadow-lg z-40 font-bold"
        >
          📹 Watch Feed
        </button>
      )}

      {/* Main Content */}
      {showFeed ? (
        <div className="relative">
          <button
            onClick={() => setShowFeed(false)}
            className="fixed top-4 left-4 bg-black/50 hover:bg-black/70 text-white px-4 py-2 rounded-lg z-50"
          >
            ← Back to Game
          </button>
          <VideoFeed />
        </div>
      ) : !gameId || !playerId ? (
        <Lobby onCreateGame={createGame} onJoinGame={joinGame} />
      ) : gameState ? (
        <GameRoom
          gameState={gameState}
          playerId={playerId}
          onSubmitCards={submitCards}
          onSelectWinner={selectWinner}
          onStartGame={startGame}
          onRequestAI={requestAIJoin}
        />
      ) : (
        <div className="min-h-screen bg-game-bg flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin text-6xl mb-4">⚙️</div>
            <p className="text-white text-xl">Loading game...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
