import React, { useState } from 'react';
import { GameStateData } from '../types/game.types';
import { BlackCard } from './BlackCard';
import { WhiteCard } from './WhiteCard';
import { CardHand } from './CardHand';
import { PlayerList } from './PlayerList';
import { VideoPlayer } from './VideoPlayer';

interface GameRoomProps {
  gameState: GameStateData;
  playerId: string;
  onSubmitCards: (cardIds: string[]) => void;
  onSelectWinner: (submissionIndex: number) => void;
  onStartGame: () => void;
  onRequestAI: (personality?: string) => void;
}

export const GameRoom: React.FC<GameRoomProps> = ({
  gameState,
  playerId,
  onSubmitCards,
  onSelectWinner,
  onStartGame,
  onRequestAI,
}) => {
  const [selectedSubmission, setSelectedSubmission] = useState<number | null>(null);

  const isCzar = gameState.current_round?.czar_id === playerId;
  const hasSubmitted = gameState.current_round?.submissions.some(
    (sub) => sub.player_id === playerId
  );

  const isLobby = gameState.state === 'lobby' || (gameState.state as string).includes('LOBBY');
  const isPlaying = gameState.state === 'playing' || (gameState.state as string).includes('PLAYING');
  const isJudging = gameState.state === 'judging' || (gameState.state as string).includes('JUDGING');
  const isRoundEnd = gameState.state === 'round_end' || (gameState.state as string).includes('ROUND_END');
  const isGameEnd = gameState.state === 'game_end' || (gameState.state as string).includes('GAME_END');
  const canStartGame = isLobby && gameState.players.length >= 3;

  return (
    <div className="min-h-screen bg-game-bg p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-game-card rounded-xl p-4 mb-4 shadow-lg">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">🎭 Absurdly Visual</h1>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-gray-400 text-sm">Game ID:</p>
                <code className="bg-game-bg px-3 py-1 rounded text-game-highlight font-mono text-sm">
                  {gameState.game_id}
                </code>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(gameState.game_id);
                    alert('Game ID copied to clipboard!');
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-2 py-1 rounded transition-all"
                  title="Copy Game ID"
                >
                  📋 Copy
                </button>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">
                {isLobby ? 'Waiting to start...' : `Round ${gameState.current_round?.round_number || 0}`}
              </div>
              <div className="text-sm text-gray-400">
                First to {gameState.points_to_win} points wins!
              </div>
            </div>
            <div>
              <button
                onClick={() => {
                  if (window.confirm('Are you sure you want to leave the game?')) {
                    window.location.reload();
                  }
                }}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-all"
              >
                🚪 Leave Game
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Left Sidebar - Players */}
          <div className="lg:col-span-1">
            <PlayerList
              players={gameState.players}
              czarId={gameState.current_round?.czar_id}
              currentPlayerId={playerId}
            />

            {isLobby && (
              <div className="mt-4 space-y-2">
                <button
                  onClick={onStartGame}
                  disabled={!canStartGame}
                  className={`
                    w-full py-3 rounded-lg font-bold transition-all duration-300
                    ${canStartGame
                      ? 'bg-game-highlight hover:bg-red-600 text-white'
                      : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    }
                  `}
                >
                  {canStartGame ? 'Start Game' : `Need ${3 - gameState.players.length} more player(s)`}
                </button>
                <button
                  onClick={() => onRequestAI('absurd')}
                  className="w-full py-2 rounded-lg font-semibold bg-purple-600 hover:bg-purple-700 text-white transition-all duration-300"
                >
                  + Add AI Bot
                </button>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-4">
            {isLobby && (
              <div className="bg-game-card rounded-xl p-8 text-center">
                <div className="text-6xl mb-4">🎮</div>
                <h2 className="text-2xl font-bold text-white mb-2">Waiting for players...</h2>
                <p className="text-gray-400">
                  Share the game ID with friends or add AI bots to start playing!
                </p>
              </div>
            )}

            {isGameEnd && (
              <div className="bg-game-card rounded-xl p-8 text-center">
                <div className="text-6xl mb-4">🏆</div>
                <h2 className="text-3xl font-bold text-white mb-4">Game Over!</h2>
                <div className="text-xl text-gray-300">
                  Winner: {gameState.players.find(p => p.score >= gameState.points_to_win)?.name}
                </div>
              </div>
            )}

            {(isPlaying || isJudging || isRoundEnd) && gameState.current_round && (
              <>
                {/* Black Card */}
                <div className="flex justify-center">
                  <div className="w-full max-w-md">
                    <BlackCard card={gameState.current_round.black_card} />
                  </div>
                </div>

                {/* Round Status */}
                <div className="bg-game-card rounded-xl p-4 text-center">
                  {isCzar && isPlaying && (
                    <p className="text-white text-lg">
                      👑 You are the Card Czar! Wait for others to submit...
                    </p>
                  )}
                  {!isCzar && isPlaying && !hasSubmitted && (
                    <p className="text-white text-lg">
                      Select your funniest card{gameState.current_round.black_card.pick > 1 ? 's' : ''}!
                    </p>
                  )}
                  {!isCzar && isPlaying && hasSubmitted && gameState.current_round && (
                    <div className="text-center py-8">
                      <div className="text-6xl mb-4">✅</div>
                      <p className="text-white text-2xl font-bold mb-4">
                        Cards Submitted!
                      </p>
                      <p className="text-gray-300 text-lg mb-2">
                        Waiting for other players...
                      </p>
                      <div className="bg-game-bg rounded-lg p-4 inline-block">
                        <p className="text-white text-xl font-semibold">
                          {gameState.current_round.submissions.length} / {gameState.players.filter(p => p.id !== gameState.current_round?.czar_id).length}
                        </p>
                        <p className="text-gray-400 text-sm">players submitted</p>
                      </div>
                    </div>
                  )}
                  {isJudging && isCzar && (
                    <p className="text-white text-lg">
                      👑 Pick the funniest combination!
                    </p>
                  )}
                  {isJudging && !isCzar && (
                    <p className="text-white text-lg">
                      Waiting for Czar to judge...
                    </p>
                  )}
                </div>

                {/* Submissions (Judging Phase) */}
                {isJudging && gameState.current_round.submissions.length > 0 && (
                  <div>
                    <h3 className="text-xl font-bold text-white mb-4">Submissions:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {gameState.current_round.submissions.map((submission, index) => (
                        <div
                          key={index}
                          onClick={() => isCzar && setSelectedSubmission(index)}
                          className={`
                            p-4 rounded-xl cursor-pointer transition-all duration-300
                            ${selectedSubmission === index ? 'bg-game-highlight' : 'bg-game-card'}
                            ${isCzar ? 'hover:scale-105' : ''}
                          `}
                        >
                          {/* Video for this submission */}
                          <div className="mb-3 rounded-lg overflow-hidden bg-gray-800">
                            {submission.video_url ? (
                              submission.video_url.includes('placeholder') ? (
                                <div className="w-full h-48 flex items-center justify-center bg-red-900/30">
                                  <p className="text-white text-center px-4">
                                    ❌ Video Generation Failed
                                  </p>
                                </div>
                              ) : (
                                <video
                                  src={submission.video_url}
                                  className="w-full h-48 object-cover"
                                  controls
                                  loop
                                  playsInline
                                />
                              )
                            ) : (
                              <div className="w-full h-48 flex items-center justify-center">
                                <div className="text-center">
                                  <div className="animate-spin text-4xl mb-2">⏳</div>
                                  <p className="text-white text-sm">Generating video...</p>
                                  <p className="text-gray-400 text-xs mt-1">Up to 90 seconds</p>
                                </div>
                              </div>
                            )}
                          </div>
                          
                          {/* Cards */}
                          <div className="space-y-2">
                            {submission.cards.map((card, cardIndex) => (
                              <WhiteCard key={cardIndex} card={card} disabled />
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                    {isCzar && selectedSubmission !== null && (
                      <div className="mt-4 text-center">
                        <button
                          onClick={() => onSelectWinner(selectedSubmission)}
                          className="bg-game-highlight hover:bg-red-600 text-white font-bold py-3 px-8 rounded-lg transition-all duration-300 transform hover:scale-105"
                        >
                          Select as Winner
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Winner Display with Video */}
                {gameState.state === 'round_end' && gameState.current_round.winner_id && (
                  <div className="space-y-4">
                    <div className="bg-game-card rounded-xl p-6 text-center">
                      <h3 className="text-2xl font-bold text-white mb-2">
                        🎉 Winner: {gameState.players.find(p => p.id === gameState.current_round?.winner_id)?.name}
                      </h3>
                    </div>
                    <VideoPlayer videoUrl={gameState.current_round.video_url} />
                  </div>
                )}

                {/* Player's Hand */}
                {!isCzar && isPlaying && !hasSubmitted && (
                  <CardHand
                    cards={gameState.your_hand}
                    onSubmit={onSubmitCards}
                    cardsToSelect={gameState.current_round.black_card.pick}
                  />
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
