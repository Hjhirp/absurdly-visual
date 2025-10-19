-- Supabase Database Schema for Absurdly Visual

-- Cards tables
-- pack column is used for both pack names and topic filtering
-- Valid pack values: 'base', 'Gaming', 'Tech', 'Sports', 'Art', 'Politics'
CREATE TABLE IF NOT EXISTS black_cards (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    pick INTEGER DEFAULT 1,
    pack TEXT DEFAULT 'base',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS white_cards (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    nsfw BOOLEAN DEFAULT FALSE,
    pack TEXT DEFAULT 'base',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for cards
CREATE INDEX IF NOT EXISTS idx_black_cards_pack ON black_cards(pack);
CREATE INDEX IF NOT EXISTS idx_white_cards_pack ON white_cards(pack);
CREATE INDEX IF NOT EXISTS idx_white_cards_nsfw ON white_cards(nsfw);

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    black_card_text TEXT NOT NULL,
    white_card_texts TEXT[] NOT NULL,
    video_url TEXT NOT NULL,
    prompt TEXT,
    game_id TEXT,
    winner_id TEXT,
    winner_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0
);

-- Likes table
CREATE TABLE IF NOT EXISTS likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(video_id, user_id)
);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    user_name TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_likes_video_id ON likes(video_id);
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_video_id ON comments(video_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);

-- RPC functions for atomic counter updates
CREATE OR REPLACE FUNCTION increment_likes(video_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE videos SET likes_count = likes_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrement_likes(video_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE videos SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_comments(video_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE videos SET comments_count = comments_count + 1 WHERE id = video_id;
END;
$$ LANGUAGE plpgsql;

-- Storage bucket for videos (run this in Supabase dashboard)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('videos', 'videos', true);

-- Row Level Security (RLS) policies
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- Allow public read access to videos
CREATE POLICY "Public videos are viewable by everyone"
ON videos FOR SELECT
USING (true);

-- Allow authenticated users to insert videos
CREATE POLICY "Authenticated users can insert videos"
ON videos FOR INSERT
WITH CHECK (true);

-- Allow public read access to likes
CREATE POLICY "Likes are viewable by everyone"
ON likes FOR SELECT
USING (true);

-- Allow anyone to like/unlike
CREATE POLICY "Anyone can like videos"
ON likes FOR INSERT
WITH CHECK (true);

CREATE POLICY "Users can unlike their own likes"
ON likes FOR DELETE
USING (true);

-- Allow public read access to comments
CREATE POLICY "Comments are viewable by everyone"
ON comments FOR SELECT
USING (true);

-- Allow anyone to comment
CREATE POLICY "Anyone can comment"
ON comments FOR INSERT
WITH CHECK (true);
