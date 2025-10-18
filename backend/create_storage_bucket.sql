-- Create videos storage buckets in Supabase
-- Run this in Supabase SQL Editor OR use the Storage UI

-- Videos bucket (for all generated videos)
INSERT INTO storage.buckets (id, name, public)
VALUES ('videos', 'videos', true)
ON CONFLICT (id) DO NOTHING;

-- Winning videos bucket (for feed)
INSERT INTO storage.buckets (id, name, public)
VALUES ('winning-videos', 'winning-videos', true)
ON CONFLICT (id) DO NOTHING;

-- Set bucket policies for videos bucket
CREATE POLICY "Public Access Videos"
ON storage.objects FOR SELECT
USING ( bucket_id = 'videos' );

CREATE POLICY "Authenticated users can upload videos"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'videos' );

-- Set bucket policies for winning-videos bucket
CREATE POLICY "Public Access Winning Videos"
ON storage.objects FOR SELECT
USING ( bucket_id = 'winning-videos' );

CREATE POLICY "Authenticated users can upload winning videos"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'winning-videos' );
