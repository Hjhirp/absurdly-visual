import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface Video {
  id: string;
  black_card_text: string;
  white_card_texts: string[];
  video_url: string;
  prompt?: string;
  winner_name?: string;
  created_at: string;
  likes_count: number;
  comments_count: number;
}

interface Comment {
  id: string;
  user_name: string;
  text: string;
  created_at: string;
}

const API_URL = 'http://localhost:8000/api/feed';

export const VideoFeed: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentText, setCommentText] = useState('');
  const [userName, setUserName] = useState('');
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);

  useEffect(() => {
    loadVideos();
  }, []);

  useEffect(() => {
    // Auto-play current video
    if (videos.length > 0 && videoRefs.current[currentIndex]) {
      videoRefs.current[currentIndex]?.play();
    }
  }, [currentIndex, videos]);

  const loadVideos = async () => {
    try {
      const response = await axios.get(`${API_URL}/videos?limit=20`);
      setVideos(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading videos:', error);
      setLoading(false);
    }
  };

  const handleLike = async (videoId: string) => {
    try {
      const userId = localStorage.getItem('userId') || `user_${Date.now()}`;
      localStorage.setItem('userId', userId);

      const response = await axios.post(`${API_URL}/like`, {
        video_id: videoId,
        user_id: userId
      });

      // Update local state
      setVideos(videos.map(v => 
        v.id === videoId 
          ? { ...v, likes_count: response.data.likes_count }
          : v
      ));
    } catch (error) {
      console.error('Error liking video:', error);
    }
  };

  const loadComments = async (videoId: string) => {
    try {
      const response = await axios.get(`${API_URL}/comments/${videoId}`);
      setComments(response.data);
      setShowComments(true);
    } catch (error) {
      console.error('Error loading comments:', error);
    }
  };

  const handleComment = async (videoId: string) => {
    if (!commentText.trim() || !userName.trim()) return;

    try {
      const userId = localStorage.getItem('userId') || `user_${Date.now()}`;
      localStorage.setItem('userId', userId);

      await axios.post(`${API_URL}/comment`, {
        video_id: videoId,
        user_id: userId,
        user_name: userName,
        text: commentText
      });

      setCommentText('');
      loadComments(videoId);

      // Update comment count
      setVideos(videos.map(v => 
        v.id === videoId 
          ? { ...v, comments_count: v.comments_count + 1 }
          : v
      ));
    } catch (error) {
      console.error('Error adding comment:', error);
    }
  };

  const handleScroll = (direction: 'up' | 'down') => {
    if (direction === 'down' && currentIndex < videos.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowComments(false);
    } else if (direction === 'up' && currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowComments(false);
    }
  };

  const handleWheel = (e: React.WheelEvent) => {
    if (e.deltaY > 0) {
      handleScroll('down');
    } else {
      handleScroll('up');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-2xl">Loading videos...</div>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-2xl">No videos yet. Play some games!</div>
      </div>
    );
  }

  const currentVideo = videos[currentIndex];

  return (
    <div 
      className="relative h-screen w-screen bg-black overflow-hidden"
      onWheel={handleWheel}
    >
      {/* Video Player */}
      <video
        ref={el => videoRefs.current[currentIndex] = el}
        src={currentVideo.video_url}
        className="absolute inset-0 w-full h-full object-contain"
        loop
        playsInline
        onClick={(e) => {
          const video = e.currentTarget;
          video.paused ? video.play() : video.pause();
        }}
      />

      {/* Overlay UI */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top Info */}
        <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/70 to-transparent">
          <div className="text-white">
            <p className="text-sm font-semibold mb-1">🎭 {currentVideo.winner_name}</p>
            <p className="text-xs opacity-80">{currentVideo.black_card_text}</p>
          </div>
        </div>

        {/* Bottom Info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/70 to-transparent">
          <div className="text-white mb-2">
            {currentVideo.white_card_texts.map((text, i) => (
              <p key={i} className="text-sm mb-1">• {text}</p>
            ))}
          </div>
        </div>

        {/* Right Side Actions */}
        <div className="absolute right-4 bottom-24 flex flex-col items-center space-y-6 pointer-events-auto">
          {/* Like Button */}
          <button
            onClick={() => handleLike(currentVideo.id)}
            className="flex flex-col items-center"
          >
            <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-2xl hover:scale-110 transition-transform">
              ❤️
            </div>
            <span className="text-white text-xs mt-1">{currentVideo.likes_count}</span>
          </button>

          {/* Comment Button */}
          <button
            onClick={() => loadComments(currentVideo.id)}
            className="flex flex-col items-center"
          >
            <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-2xl hover:scale-110 transition-transform">
              💬
            </div>
            <span className="text-white text-xs mt-1">{currentVideo.comments_count}</span>
          </button>

          {/* Share Button */}
          <button className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-2xl hover:scale-110 transition-transform">
              📤
            </div>
          </button>
        </div>

        {/* Navigation Arrows */}
        {currentIndex > 0 && (
          <button
            onClick={() => handleScroll('up')}
            className="absolute top-1/2 left-4 transform -translate-y-1/2 text-white text-4xl pointer-events-auto opacity-50 hover:opacity-100"
          >
            ↑
          </button>
        )}
        {currentIndex < videos.length - 1 && (
          <button
            onClick={() => handleScroll('down')}
            className="absolute top-1/2 right-4 transform -translate-y-1/2 text-white text-4xl pointer-events-auto opacity-50 hover:opacity-100"
          >
            ↓
          </button>
        )}
      </div>

      {/* Comments Panel */}
      {showComments && (
        <div className="absolute bottom-0 left-0 right-0 h-2/3 bg-black/90 backdrop-blur p-4 overflow-y-auto pointer-events-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-white text-xl font-bold">Comments</h3>
            <button
              onClick={() => setShowComments(false)}
              className="text-white text-2xl"
            >
              ✕
            </button>
          </div>

          {/* Comment Input */}
          <div className="mb-4 space-y-2">
            <input
              type="text"
              placeholder="Your name"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              className="w-full px-4 py-2 rounded-lg bg-white/10 text-white placeholder-gray-400 border border-white/20"
            />
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Add a comment..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleComment(currentVideo.id)}
                className="flex-1 px-4 py-2 rounded-lg bg-white/10 text-white placeholder-gray-400 border border-white/20"
              />
              <button
                onClick={() => handleComment(currentVideo.id)}
                className="px-6 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700"
              >
                Post
              </button>
            </div>
          </div>

          {/* Comments List */}
          <div className="space-y-3">
            {comments.map((comment) => (
              <div key={comment.id} className="bg-white/5 rounded-lg p-3">
                <p className="text-white font-semibold text-sm">{comment.user_name}</p>
                <p className="text-gray-300 text-sm mt-1">{comment.text}</p>
                <p className="text-gray-500 text-xs mt-1">
                  {new Date(comment.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
