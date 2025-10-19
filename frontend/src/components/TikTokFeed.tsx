import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface FeedVideo {
  id: string;
  black_card_text: string;
  white_card_texts: string[];
  video_url: string;
  image_url?: string;
  narration_audio_url?: string;
  winner_name?: string;
  likes: number;
  views: number;
  created_at: string;
}

export const TikTokFeed: React.FC = () => {
  const [videos, setVideos] = useState<FeedVideo[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/feed/videos?limit=20`);
      setVideos(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching videos:', error);
      setLoading(false);
    }
  };

  const handleScroll = (direction: 'up' | 'down') => {
    if (direction === 'down' && currentIndex < videos.length - 1) {
      setCurrentIndex(currentIndex + 1);
      trackView(videos[currentIndex + 1].id);
    } else if (direction === 'up' && currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const trackView = async (videoId: string) => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/api/feed/view/${videoId}`);
    } catch (error) {
      console.error('Error tracking view:', error);
    }
  };

  const handleLike = async (videoId: string) => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/api/feed/like`, {
        video_id: videoId,
        user_id: 'anonymous'
      });
      // Update local state
      setVideos(videos.map(v => 
        v.id === videoId ? { ...v, likes: v.likes + 1 } : v
      ));
    } catch (error) {
      console.error('Error liking video:', error);
    }
  };

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') handleScroll('down');
      if (e.key === 'ArrowUp') handleScroll('up');
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentIndex, videos.length]);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-game-bg">
        <div className="text-white text-2xl">Loading feed...</div>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="h-screen flex items-center justify-center bg-game-bg">
        <div className="text-center">
          <div className="text-6xl mb-4">🎮</div>
          <div className="text-white text-2xl mb-2">No videos yet!</div>
          <div className="text-gray-400">Play some games to create content</div>
        </div>
      </div>
    );
  }

  const currentVideo = videos[currentIndex];

  return (
    <div 
      ref={containerRef}
      className="h-screen w-full bg-black overflow-hidden relative snap-y snap-mandatory"
    >
      {/* Video Container */}
      <div className="h-full w-full flex items-center justify-center relative">
        {/* Video or Image */}
        {currentVideo.video_url ? (
          <video
            key={currentVideo.id}
            src={currentVideo.video_url}
            className="h-full w-auto max-w-full object-contain"
            autoPlay
            loop
            playsInline
            muted={false}
          />
        ) : currentVideo.image_url ? (
          <img
            src={currentVideo.image_url}
            alt="Generated scene"
            className="h-full w-auto max-w-full object-contain"
          />
        ) : (
          <div className="text-white text-xl">No media available</div>
        )}

        {/* Overlay Content */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 to-transparent">
          {/* Question */}
          <div className="mb-4">
            <p className="text-white text-lg font-bold mb-2">
              {currentVideo.black_card_text}
            </p>
            {/* Answer */}
            <div className="flex flex-wrap gap-2">
              {currentVideo.white_card_texts.map((card, idx) => (
                <span key={idx} className="bg-game-highlight px-3 py-1 rounded-full text-white text-sm">
                  {card}
                </span>
              ))}
            </div>
          </div>

          {/* Winner */}
          {currentVideo.winner_name && (
            <p className="text-gray-300 text-sm mb-2">
              👑 Winner: {currentVideo.winner_name}
            </p>
          )}

          {/* Stats */}
          <div className="flex items-center gap-4 text-white text-sm">
            <span>❤️ {currentVideo.likes}</span>
            <span>👁️ {currentVideo.views}</span>
          </div>
        </div>

        {/* Right Side Actions */}
        <div className="absolute right-4 bottom-32 flex flex-col gap-6">
          {/* Like Button */}
          <button
            onClick={() => handleLike(currentVideo.id)}
            className="flex flex-col items-center gap-1 text-white hover:scale-110 transition-transform"
          >
            <div className="w-12 h-12 rounded-full bg-game-card flex items-center justify-center text-2xl">
              ❤️
            </div>
            <span className="text-xs">{currentVideo.likes}</span>
          </button>

          {/* Audio Button */}
          {currentVideo.narration_audio_url && (
            <button
              onClick={() => {
                const audio = new Audio(currentVideo.narration_audio_url);
                audio.play();
              }}
              className="flex flex-col items-center gap-1 text-white hover:scale-110 transition-transform"
            >
              <div className="w-12 h-12 rounded-full bg-game-card flex items-center justify-center text-2xl">
                🎙️
              </div>
              <span className="text-xs">Audio</span>
            </button>
          )}
        </div>

        {/* Navigation Arrows - Up/Down Only */}
        {currentIndex > 0 && (
          <button
            onClick={() => handleScroll('up')}
            className="absolute top-8 left-1/2 transform -translate-x-1/2 bg-black/60 hover:bg-black/80 text-white w-14 h-14 rounded-full flex items-center justify-center text-3xl hover:scale-110 transition-all shadow-lg backdrop-blur-sm"
            aria-label="Previous video"
          >
            ↑
          </button>
        )}
        {currentIndex < videos.length - 1 && (
          <button
            onClick={() => handleScroll('down')}
            className="absolute bottom-24 left-1/2 transform -translate-x-1/2 bg-black/60 hover:bg-black/80 text-white w-14 h-14 rounded-full flex items-center justify-center text-3xl hover:scale-110 transition-all shadow-lg backdrop-blur-sm"
            aria-label="Next video"
          >
            ↓
          </button>
        )}

        {/* Progress Indicator */}
        <div className="absolute top-4 right-4 text-white text-sm bg-black/50 px-3 py-1 rounded-full">
          {currentIndex + 1} / {videos.length}
        </div>
      </div>
    </div>
  );
};
