\echo 'Starting initialization script...'

-- Drop existing tables to ensure a clean schema
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS channels CASCADE;
DROP TYPE IF EXISTS sentiment_type;

-- Create channels table with updated schema
CREATE TABLE IF NOT EXISTS channels (
    channel_id VARCHAR(255) PRIMARY KEY,
    channel_name VARCHAR(255),
    views INTEGER,
    total_videos INTEGER,
    subscribers INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- fixed ENUM type to include 'error' sentiment
CREATE TYPE sentiment_type AS ENUM ('positive', 'negative', 'neutral', 'unknown', 'error');

CREATE TABLE videos (
    video_id VARCHAR(255) PRIMARY KEY,
    channel_id VARCHAR(255),
    channel_name VARCHAR(255),
    title VARCHAR(255),
    published_at TIMESTAMP,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    duration INTEGER,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

CREATE TABLE comments (
    comment_id VARCHAR(255) PRIMARY KEY,
    video_id VARCHAR(255),
    channel_id VARCHAR(255),
    comment_text TEXT,
    published_at TIMESTAMP,
    vader_score DECIMAL(4, 3),
    vader_sentiment sentiment_type,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);