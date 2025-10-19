-- Supabase Storage Setup
-- Run this in Supabase SQL Editor

-- Create images bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('images', 'images', true)
ON CONFLICT (id) DO NOTHING;

-- Create audio bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('audio', 'audio', true)
ON CONFLICT (id) DO NOTHING;

-- Create videos bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('videos', 'videos', true)
ON CONFLICT (id) DO NOTHING;

-- Policies for images bucket
CREATE POLICY "Public Access Images"
ON storage.objects FOR SELECT
USING (bucket_id = 'images');

CREATE POLICY "Anon Upload Images"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'images');

-- Policies for audio bucket
CREATE POLICY "Public Access Audio"
ON storage.objects FOR SELECT
USING (bucket_id = 'audio');

CREATE POLICY "Anon Upload Audio"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'audio');

-- Policies for videos bucket
CREATE POLICY "Public Access Videos"
ON storage.objects FOR SELECT
USING (bucket_id = 'videos');

CREATE POLICY "Anon Upload Videos"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'videos');
