-- CodeBot AI Database Initialization Script
-- PostgreSQL Schema for Git Data

-- Commits table
CREATE TABLE IF NOT EXISTS commits (
    sha VARCHAR(40) PRIMARY KEY,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    commit_date TIMESTAMP,
    message TEXT,
    files_changed INTEGER DEFAULT 0,
    insertions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File changes table
CREATE TABLE IF NOT EXISTS file_changes (
    id SERIAL PRIMARY KEY,
    commit_sha VARCHAR(40) REFERENCES commits(sha) ON DELETE CASCADE,
    filepath VARCHAR(500),
    change_type VARCHAR(20),
    insertions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table (for future authentication)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table (for chat history)
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(100) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table (for chat messages)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(100) REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_commits_date ON commits(commit_date DESC);
CREATE INDEX IF NOT EXISTS idx_commits_author ON commits(author_name);
CREATE INDEX IF NOT EXISTS idx_file_changes_path ON file_changes(filepath);
CREATE INDEX IF NOT EXISTS idx_file_changes_commit ON file_changes(commit_sha);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Insert sample data (optional - for testing)
-- INSERT INTO users (username, email) VALUES ('admin', 'admin@codebot.ai');

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'CodeBot AI database initialized successfully!';
END
$$;
