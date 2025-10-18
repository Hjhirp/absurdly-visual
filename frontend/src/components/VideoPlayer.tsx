import React, { useRef, useEffect } from 'react';

interface VideoPlayerProps {
  videoUrl: string | null;
  onEnded?: () => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, onEnded }) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current && videoUrl) {
      videoRef.current.load();
      videoRef.current.play().catch((error) => {
        console.error('Error playing video:', error);
      });
    }
  }, [videoUrl]);

  if (!videoUrl) {
    return (
      <div className="w-full aspect-video bg-game-bg rounded-xl flex items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse-slow text-6xl mb-4">🎬</div>
          <p className="text-white text-xl font-semibold">Generating video...</p>
          <p className="text-gray-400 mt-2">This may take a moment</p>
        </div>
      </div>
    );
  }

  // Check if it's a mock video
  const isMock = videoUrl.includes('placeholder');

  return (
    <div className="w-full aspect-video bg-black rounded-xl overflow-hidden shadow-2xl">
      {isMock ? (
        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-900 to-blue-900">
          <div className="text-center p-8">
            <div className="text-8xl mb-4 animate-bounce-in">🎥</div>
            <p className="text-white text-2xl font-bold mb-2">Video Generated!</p>
            <p className="text-gray-300 text-sm">(Mock video - Connect Veo3 API for real videos)</p>
            <div className="mt-4 text-xs text-gray-400 font-mono">{videoUrl}</div>
          </div>
        </div>
      ) : (
        <video
          ref={videoRef}
          className="w-full h-full object-contain"
          controls
          onEnded={onEnded}
        >
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      )}
    </div>
  );
};
